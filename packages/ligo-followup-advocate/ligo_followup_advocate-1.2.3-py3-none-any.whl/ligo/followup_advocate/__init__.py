import os
import shutil
import tempfile
import urllib
import webbrowser

import astropy.coordinates as coord
import astropy.time
import astropy.units as u
import healpy as hp
import lxml.etree
import numpy as np
from astropy.io.fits import getheader
from ligo.gracedb import rest
from ligo.skymap.io.fits import read_sky_map
from ligo.skymap.postprocess.ellipse import find_ellipse
from ligo.skymap.postprocess.crossmatch import crossmatch

from .jinja import env
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions


def authors(authors, service=rest.DEFAULT_SERVICE_URL):
    """Write GCN Circular author list"""
    return env.get_template('authors.jinja2').render(authors=authors).strip()


def guess_skyloc_pipeline(filename):
    keys = ['cWB', 'BAYESTAR', 'Bilby', 'LIB', 'LALInference',
            'oLIB', 'MLy', 'UNKNOWN']
    skyloc_pipelines_dict = dict(zip([x.lower() for x in keys], keys))
    skyloc_pipelines_dict['rapidpe_rift'] = 'RapidPE-RIFT'
    try:
        return skyloc_pipelines_dict[filename.split('.')[0].lower()]
    except KeyError:
        return filename.split('.')[0]


def main_dict(gracedb_id, client):
    """Create general dictionary to pass to compose circular"""

    event = client.superevent(gracedb_id).json()
    preferred_event = event['preferred_event_data']
    preferred_pipeline = preferred_event['pipeline']
    early_warning_pipelines = []
    pipelines = []
    gw_events = event['gw_events']
    early_warning_alert = False

    for gw_event in gw_events:
        gw_event_dict = client.event(gw_event).json()
        pipeline = gw_event_dict['pipeline']
        search = gw_event_dict['search']
        if pipeline not in pipelines:
            pipelines.append(pipeline)
        if pipeline not in early_warning_pipelines and \
                search == 'EarlyWarning':
            early_warning_pipelines.append(pipeline)
    # Sort to get alphabetical order
    pipelines.sort()
    early_warning_pipelines.sort()

    voevents = client.voevents(gracedb_id).json()['voevents']
    if not voevents:
        raise ValueError(
            "{} has no VOEvent to generate circulars from.".format(
                gracedb_id))

    citation_index = {pipeline.lower(): pipelines.index(pipeline) + 1 for
                      pipeline in pipelines}
    for pipeline in early_warning_pipelines:
        if pipeline.lower() != 'mbta':
            citation_index[pipeline.lower() + '_earlywarning'] = \
                max(citation_index.values()) + 1

    gpstime = float(preferred_event['gpstime'])
    event_time = astropy.time.Time(gpstime, format='gps').utc

    # Grab latest p_astro and em_bright files
    superevent_files = client.files(gracedb_id).json()
    em_brightfilename = 'em_bright'
    p_astrofilename = 'p_astro'
    em_brightfiles = []
    p_astrofiles = []

    for file in superevent_files:
        if em_brightfilename in file and '.png' not in file:
            em_brightfiles.append(file)
        elif p_astrofilename in file and '.png' not in file:
            p_astrofiles.append(file)

    if em_brightfiles:
        source_classification = client.files(
            gracedb_id, em_brightfiles[-1]).json()
        source_classification = {
            key: 100 * value for key, value in source_classification.items()}
        citation_index['em_bright'] = max(citation_index.values()) + 1
    else:
        source_classification = {}

    if p_astrofiles:
        classifications = client.files(
            gracedb_id, p_astrofiles[-1]).json()
        classifications = {
            key: 100 * value for key, value in classifications.items()}
    else:
        classifications = {}

    skymaps = {}
    for voevent in voevents:
        voevent_text = client.files(gracedb_id, voevent['filename']).read()
        root = lxml.etree.fromstring(voevent_text)
        alert_type = root.find(
            './What/Param[@name="AlertType"]').attrib['value'].lower()
        if alert_type == 'earlywarning':
            # Add text for early warning detection if one early warning alert
            early_warning_alert = True
        url = root.find('./What/Group/Param[@name="skymap_fits"]')
        if url is None:
            continue
        url = url.attrib['value']
        _, filename = os.path.split(url)
        skyloc_pipeline = guess_skyloc_pipeline(filename)
        issued_time = astropy.time.Time(root.find('./Who/Date').text).gps
        if filename not in skymaps:
            skymaps[filename] = dict(
                alert_type=alert_type,
                pipeline=skyloc_pipeline,
                filename=filename,
                latency=issued_time-event_time.gps)
            if skyloc_pipeline.lower() not in citation_index:
                citation_index[skyloc_pipeline.lower()] = \
                    max(citation_index.values()) + 1
    skymaps = list(skymaps.values())

    o = urllib.parse.urlparse(client.service_url)

    kwargs = dict(
        subject='Identification',
        gracedb_id=gracedb_id,
        gracedb_service_url=urllib.parse.urlunsplit(
            (o.scheme, o.netloc, '/superevents/', '', '')),
        group=preferred_event['group'],
        pipeline=preferred_pipeline,
        all_pipelines=pipelines,
        early_warning_alert=early_warning_alert,
        early_warning_pipelines=early_warning_pipelines,
        gpstime='{0:.03f}'.format(round(float(preferred_event['gpstime']), 3)),
        search=preferred_event.get('search', ''),
        far=preferred_event['far'],
        utctime=event_time.iso,
        instruments=preferred_event['instruments'].split(','),
        skymaps=skymaps,
        prob_has_ns=source_classification.get('HasNS'),
        prob_has_remnant=source_classification.get('HasRemnant'),
        prob_has_massgap=source_classification.get('HasMassGap'),
        include_ellipse=None,
        classifications=classifications,
        citation_index=citation_index)

    if skymaps:
        preferred_skymap = skymaps[-1]['filename']
        cl = 90
        include_ellipse, ra, dec, a, b, pa, area, greedy_area = \
            uncertainty_ellipse(gracedb_id, preferred_skymap, client, cl=cl)
        kwargs.update(
            preferred_skymap=preferred_skymap,
            cl=cl,
            include_ellipse=include_ellipse,
            ra=coord.Longitude(ra*u.deg),
            dec=coord.Latitude(dec*u.deg),
            a=coord.Angle(a*u.deg),
            b=coord.Angle(b*u.deg),
            pa=coord.Angle(pa*u.deg),
            ellipse_area=area,
            greedy_area=greedy_area)
        try:
            distmu, distsig = get_distances_skymap_gracedb(gracedb_id,
                                                           preferred_skymap,
                                                           client)
            kwargs.update(
                distmu=distmu,
                distsig=distsig)
        except TypeError:
            pass

    return kwargs


def compose(gracedb_id, authors=(), mailto=False,
            service=rest.DEFAULT_SERVICE_URL, client=None):
    """Compose GCN Circular draft"""

    if client is None:
        client = rest.GraceDb(service)

    kwargs = main_dict(gracedb_id, client=client)
    kwargs.update(authors=authors)
    kwargs.update(change_significance_statement=False)

    subject = env.get_template('subject.jinja2').render(**kwargs).strip()
    body = env.get_template('initial_circular.jinja2').render(**kwargs).strip()

    if mailto:
        pattern = 'mailto:emfollow@ligo.org,dac@ligo.org?subject={0}&body={1}'
        url = pattern.format(
            urllib.parse.quote(subject),
            urllib.parse.quote(body))
        webbrowser.open(url)
    else:
        return '{0}\n\n{1}'.format(subject, body)


def compose_raven(gracedb_id, authors=(),
                  service=rest.DEFAULT_SERVICE_URL, client=None):
    """Compose EM_COINC RAVEN GCN Circular draft"""

    if client is None:
        client = rest.GraceDb(service)

    kwargs = dict()
    kwargs = _update_raven_parameters(gracedb_id, kwargs, client)
    kwargs.update(main_dict(gracedb_id, client=client))
    kwargs.update(update_alert=False)

    subject = (
        env.get_template('RAVEN_subject.jinja2').render(**kwargs)
        .strip())
    body = (
        env.get_template('RAVEN_circular.jinja2').render(**kwargs)
        .strip())
    return '{0}\n\n{1}'.format(subject, body)


def compose_llama(
        gracedb_id, authors=(), service=rest.DEFAULT_SERVICE_URL,
        icecube_alert=None,
        client=None):
    """Compose GRB LLAMA GCN Circular draft.
    Here, gracedb_id will be a GRB superevent ID in GraceDb."""

    if client is None:
        client = rest.GraceDb(service)

    superevent = client.superevent(gracedb_id).json()

    gpstime = float(superevent['t_0'])
    tl, th = gpstime - 500, gpstime + 500
    event_time = astropy.time.Time(gpstime, format='gps').utc
    tl_datetime = str(astropy.time.Time(
                      tl, format='gps').isot).replace('T', ' ')
    th_datetime = str(astropy.time.Time(
                      th, format='gps').isot).replace('T', ' ')

    o = urllib.parse.urlparse(client.service_url)
    kwargs = dict(
        gracedb_service_url=urllib.parse.urlunsplit(
            (o.scheme, o.netloc, '/events/', '', '')),
        gracedb_id=gracedb_id,
        llama=True,
        icecube_alert=icecube_alert,
        event_time=event_time,
        tl_datetime=tl_datetime,
        th_datetime=th_datetime,
        authors=authors)

    citation_index = {'llama': 1, 'llama_stat': 2}
    kwargs.update(citation_index=citation_index)

    files = client.files(gracedb_id).json()

    llama_stat_filename = 'significance_subthreshold_lvc-i3.json'
    if llama_stat_filename in files:
        llama_stat_file = client.files(gracedb_id, llama_stat_filename).json()
        llama_fap = llama_stat_file["p_value"]
        neutrinos = llama_stat_file["inputs"]["neutrino_info"]
        lines = []
        for neutrino in neutrinos:
            # Build aligned string
            vals = []
            dt = (event_time -
                  astropy.time.Time(neutrino['mjd'],
                                    format='mjd')).to(u.s).value
            vals.append('{:.2f}'.format(dt))
            vals.append('{:.2f}'.format(neutrino['ra']))
            vals.append('{:.2f}'.format(neutrino['dec']))
            vals.append('{:.2f}'.format(neutrino['sigma']))
            vals.append('{:.4f}'.format(llama_fap))
            lines.append(align_number_string(vals, [0, 11, 21, 40, 59]))

        kwargs.update(llama_fap=llama_fap,
                      neutrinos=lines)

    subject = (
        env.get_template('llama_subject.jinja2').render(**kwargs)
        .strip())
    if icecube_alert:
        body = (
            env.get_template('llama_alert_circular.jinja2').render(**kwargs)
            .strip())
    else:
        body = (
            env.get_template('llama_track_circular.jinja2').render(**kwargs)
            .strip())
    return '{0}\n\n{1}'.format(subject, body)


def compose_grb_medium_latency(
        gracedb_id, authors=(), service=rest.DEFAULT_SERVICE_URL, client=None):
    """Compose GRB Medium Latency GCN Circular draft.
    Here, gracedb_id will be a GRB external trigger ID in GraceDb."""

    if client is None:
        client = rest.GraceDb(service)

    event = client.event(gracedb_id).json()
    search = event['search']

    if search != 'GRB':
        return

    group = event['group']
    pipeline = event['pipeline']
    external_trigger = event['extra_attributes']['GRB']['trigger_id']

    o = urllib.parse.urlparse(client.service_url)
    kwargs = dict(
        gracedb_service_url=urllib.parse.urlunsplit(
            (o.scheme, o.netloc, '/events/', '', '')),
        gracedb_id=gracedb_id,
        group=group,
        grb=True,
        pipeline=pipeline,
        external_trigger=external_trigger,
        exclusions=[],
        detections=[])

    files = client.files(gracedb_id).json()

    citation_index = {}
    index = 1
    xpipeline_fap_file = 'false_alarm_probability_x.json'
    if xpipeline_fap_file in files:
        xpipeline_fap = client.files(gracedb_id, xpipeline_fap_file).json()
        online_xpipeline_fap = xpipeline_fap.get('Online Xpipeline')
        if online_xpipeline_fap < 0.001:
            kwargs['detections'].append('xpipeline')
            kwargs.update(online_xpipeline_fap=online_xpipeline_fap)
        else:
            kwargs['exclusions'].append('xpipeline')
            xpipeline_distances_file = 'distances_x.json'
            xpipeline_distances = client.files(gracedb_id,
                                               xpipeline_distances_file).json()
            burst_exclusion = xpipeline_distances.get('Burst Exclusion')
            kwargs.update(burst_exclusion=burst_exclusion)
        citation_index['xpipeline'] = index
        index += 1

    pygrb_fap_file = 'false_alarm_probability_pygrb.json'
    if pygrb_fap_file in files:
        pygrb_fap = client.files(gracedb_id, pygrb_fap_file).json()
        online_pygrb_fap = pygrb_fap.get('Online PyGRB')
        if online_pygrb_fap < 0.01:
            kwargs['detections'].append('pygrb')
            kwargs.update(online_pygrb_fap=online_pygrb_fap)
        else:
            kwargs['exclusions'].append('pygrb')
            pygrb_distances_file = 'distances_pygrb.json'
            pygrb_distances = client.files(gracedb_id,
                                           pygrb_distances_file).json()
            nsns_exclusion = pygrb_distances.get('NSNS Exclusion')
            nsbh_exclusion = pygrb_distances.get('NSBH Exclusion')
            kwargs.update(nsbh_exclusion=nsbh_exclusion,
                          nsns_exclusion=nsns_exclusion)
        citation_index['pygrb'] = index

    kwargs.update(citation_index=citation_index)

    subject = (
        env.get_template('medium_latency_grb_subject.jinja2').render(**kwargs)
        .strip())
    body = (
        env.get_template('medium_latency_grb_circular.jinja2').render(**kwargs)
        .strip())
    return '{0}\n\n{1}'.format(subject, body)


def compose_update(gracedb_id, authors=(),
                   service=rest.DEFAULT_SERVICE_URL,
                   update_types=['sky_localization', 'p_astro',
                                 'em_bright', 'raven'],
                   client=None):
    """Compose GCN update circular"""
    if client is None:
        client = rest.GraceDb(service)

    kwargs = main_dict(gracedb_id, client=client)
    kwargs.pop('citation_index', None)

    # Adjust files for update type alert
    citation_index = {}
    skymaps = []
    index = 1
    if 'em_bright' in update_types or 'sky_localization' in update_types:
        updated_skymap = kwargs.get('skymaps')[-1]
        kwargs.update(updated_skymap=updated_skymap)
        citation_index[updated_skymap['pipeline'].lower()] = index
        skymaps = [updated_skymap]
        if 'em_bright' in update_types:
            index += 1
            citation_index['em_bright'] = index

    kwargs.update(skymaps=skymaps,
                  citation_index=citation_index,
                  all_pipelines=[],
                  update_alert=True)

    if 'raven' in update_types:
        kwargs = _update_raven_parameters(gracedb_id, kwargs, client)

    kwargs.update(authors=authors)
    kwargs.update(change_significance_statement=False)
    kwargs.update(subject='Update')
    kwargs.update(update_types=update_types)

    subject = env.get_template('subject.jinja2').render(**kwargs).strip()
    body = env.get_template(
               'update_circular.jinja2').render(**kwargs).strip()
    return '{0}\n\n{1}'.format(subject, body)


def compose_retraction(gracedb_id, authors=(),
                       service=rest.DEFAULT_SERVICE_URL, client=None):
    """Compose GCN retraction circular"""
    if client is None:
        client = rest.GraceDb(service)
    event = client.superevent(gracedb_id).json()
    preferred_event = event['preferred_event_data']
    labels = event['labels']
    earlywarning = \
        ('EARLY_WARNING' in labels and
         {'EM_SelectedConfident', 'SIGNIF_LOCKED'}.isdisjoint(labels))

    kwargs = dict(
                 subject='Retraction',
                 gracedb_id=gracedb_id,
                 group=preferred_event['group'],
                 earlywarning=earlywarning,
                 authors=authors
             )

    subject = env.get_template('subject.jinja2').render(**kwargs).strip()
    body = env.get_template('retraction.jinja2').render(**kwargs).strip()
    return '{0}\n\n{1}'.format(subject, body)


def read_map_gracedb(graceid, filename, client):
    with tempfile.NamedTemporaryFile(mode='w+b') as localfile:
        remotefile = client.files(graceid, filename, raw=True)
        shutil.copyfileobj(remotefile, localfile)
        localfile.flush()
        return read_sky_map(localfile.name, moc=True)


def get_distances_skymap_gracedb(graceid, filename, client):
    with tempfile.NamedTemporaryFile(mode='w+b') as localfile:
        remotefile = client.files(graceid, filename, raw=True)
        shutil.copyfileobj(remotefile, localfile)
        localfile.flush()
        header = getheader(localfile.name, 1)
        try:
            return header['distmean'], header['diststd']
        except KeyError:
            pass


def read_map_from_path(path, client):
    return read_map_gracedb(*path.split('/'), client)[0]


def align_number_string(nums, positions):
    positions.append(len(nums[-1]))
    gen = (val + ' ' * (positions[i+1]-positions[i]-len(val))
           for i, val in enumerate(nums))
    return ''.join(gen)


def mask_cl(p, level=90):
    pflat = p.ravel()
    i = np.flipud(np.argsort(p))
    cs = np.cumsum(pflat[i])
    cls = np.empty_like(pflat)
    cls[i] = cs
    cls = cls.reshape(p.shape)
    return cls <= 1e-2 * level


def compare_skymaps(paths, service=rest.DEFAULT_SERVICE_URL, client=None):
    """Produce table of sky map overlaps"""
    if client is None:
        client = rest.GraceDb(service)
    filenames = [path.split('/')[1] for path in paths]
    pipelines = [guess_skyloc_pipeline(filename) for filename in filenames]
    probs = [read_map_from_path(path, client) for path in paths]
    npix = max(len(prob) for prob in probs)
    nside = hp.npix2nside(npix)
    deg2perpix = hp.nside2pixarea(nside, degrees=True)
    probs = [hp.ud_grade(prob, nside, power=-2) for prob in probs]
    masks = [mask_cl(prob) for prob in probs]
    areas = [mask.sum() * deg2perpix for mask in masks]
    joint_areas = [(mask & masks[-1]).sum() * deg2perpix for mask in masks]

    kwargs = dict(params=zip(filenames, pipelines, areas, joint_areas))

    return env.get_template('compare_skymaps.jinja2').render(**kwargs)


def uncertainty_ellipse(graceid, filename, client, cl=90,
                        ratio_ellipse_cl_areas=1.35):
    """Compute uncertainty ellipses for a given sky map

    Parameters
    ----------
    graceid: str
        ID of the trigger used by GraceDB
    filename: str
        File name of sky map
    client: class
        REST API client for HTTP connection
    cl: float
        Percentage of minimal credible area
    ratio_ellipse_cl_areas: float
        Ratio between ellipse area and minimal credible area from cl
    """
    if filename.endswith('.gz'):
        # Try using the multi-res sky map if it exists
        try:
            new_filename = filename.replace('.fits.gz', '.multiorder.fits')
            skymap = read_map_gracedb(graceid, new_filename, client)
        except (IOError, rest.HTTPError):
            skymap = read_map_gracedb(graceid, filename, client)
    else:
        skymap = read_map_gracedb(graceid, filename, client)

    result = crossmatch(skymap, contours=[cl / 100])
    greedy_area = result.contour_areas[0]
    ra, dec, a, b, pa, ellipse_area = find_ellipse(skymap, cl=cl)
    return ellipse_area <= ratio_ellipse_cl_areas*greedy_area, ra, dec, a, b, \
        pa, ellipse_area, greedy_area


def _update_raven_parameters(gracedb_id, kwargs, client):
    """Update kwargs with parameters for RAVEN coincidence"""

    event = client.superevent(gracedb_id).json()

    if 'EM_COINC' not in event['labels']:
        raise ValueError("No EM_COINC label for {}".format(gracedb_id))

    preferred_event = event['preferred_event_data']
    group = preferred_event['group']
    gpstime = float(preferred_event['gpstime'])
    event_time = astropy.time.Time(gpstime, format='gps').utc

    em_event_id = event['em_type']
    em_event = client.event(em_event_id).json()
    em_event_gpstime = float(em_event['gpstime'])
    external_pipeline = em_event['pipeline']
    # Get all other pipelines, removing duplicates
    other_ext_pipelines = \
        [*set(client.event(id).json()['pipeline'] for id
              in event['em_events'])]
    # Remove preferred pipeline
    other_ext_pipelines.remove(external_pipeline)
    # FIXME in GraceDb: Even SNEWS triggers have an extra attribute GRB.
    external_trigger_id = em_event['extra_attributes']['GRB']['trigger_id']
    snews = (em_event['pipeline'] == 'SNEWS')
    grb = (em_event['search'] in ['GRB', 'SubGRB', 'SubGRBTargeted', 'MDC']
           and not snews)
    subthreshold = em_event['search'] in ['SubGRB', 'SubGRBTargeted']
    subthreshold_targeted = em_event['search'] == 'SubGRBTargeted'
    far_grb = em_event['far']

    o = urllib.parse.urlparse(client.service_url)
    kwargs.update(
        gracedb_service_url=urllib.parse.urlunsplit(
            (o.scheme, o.netloc, '/superevents/', '', '')),
        gracedb_id=gracedb_id,
        group=group,
        external_pipeline=external_pipeline,
        external_trigger=external_trigger_id,
        snews=snews,
        grb=grb,
        subthreshold=subthreshold,
        subthreshold_targeted=subthreshold_targeted,
        other_ext_pipelines=other_ext_pipelines,
        far_grb=far_grb,
        latency=abs(round(em_event_gpstime-gpstime, 1)),
        beforeafter='before' if gpstime > em_event_gpstime else 'after')

    if grb:
        # Grab GRB coincidence FARs
        time_coinc_far = event['time_coinc_far']
        space_time_coinc_far = event['space_coinc_far']
        kwargs.update(
            time_coinc_far=time_coinc_far,
            space_time_coinc_far=space_time_coinc_far,
            ext_ra=em_event['extra_attributes']['GRB']['ra'],
            ext_dec=em_event['extra_attributes']['GRB']['dec'],
            ext_error=em_event['extra_attributes']['GRB']['error_radius'])

        # Find combined sky maps for GRB
        voevents = client.voevents(gracedb_id).json()['voevents']
        combined_skymaps = {}
        if not voevents:
            raise ValueError(
                "{} has no VOEvent to generate circulars from.".format(
                    gracedb_id))
        for i, voevent in enumerate(voevents):
            voevent_text = client.files(gracedb_id, voevent['filename']).read()
            root = lxml.etree.fromstring(voevent_text)
            alert_type = root.find(
                './What/Param[@name="AlertType"]').attrib['value'].lower()
            # Check if significant GW alert already queued or sent
            change_significance_statement = \
                {'EM_SelectedConfident', 'SIGNIF_LOCKED'}.isdisjoint(
                    event['labels'])
            url = root.find('./What/Group/Param[@name="joint_skymap_fits"]')
            if url is None:
                continue
            url = url.attrib['value']
            _, filename = os.path.split(url)
            issued_time = astropy.time.Time(
                              root.find('./Who/Date').text).gps
            if filename not in combined_skymaps:
                combined_skymaps[filename] = dict(
                    alert_type=alert_type,
                    filename=filename,
                    latency=issued_time-event_time.gps)

        if combined_skymaps:
            combined_skymaps = list(combined_skymaps.values())
            combined_skymap = combined_skymaps[-1]['filename']
            cl = 90
            include_ellipse, ra, dec, a, b, pa, area, greedy_area = \
                uncertainty_ellipse(gracedb_id, combined_skymap, client, cl=cl)
            kwargs.update(
                combined_skymap=combined_skymap,
                combined_skymaps=combined_skymaps,
                cl=cl,
                combined_skymap_include_ellipse=include_ellipse,
                combined_skymap_ra=coord.Longitude(ra*u.deg),
                combined_skymap_dec=coord.Latitude(dec*u.deg),
                combined_skymap_a=coord.Angle(a*u.deg),
                combined_skymap_b=coord.Angle(b*u.deg),
                combined_skymap_pa=coord.Angle(pa*u.deg),
                combined_skymap_ellipse_area=area,
                combined_skymap_greedy_area=greedy_area,
                change_significance_statement=change_significance_statement)

    return kwargs
