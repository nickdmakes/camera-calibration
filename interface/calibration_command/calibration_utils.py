from interface.session.models.settings_model import SettingsModel
from interface.session.models.lens_encoder_model import LensEncoderModel

def generate_focus_points(settings: SettingsModel, lem: LensEncoderModel):
    '''
    Generate focus points for the calibration image gathering process.
    @param settings: CalibrationSettings object
    @param lem: LensEncoderMap object
    '''
    # generate a list of integers from 1 to 10000 (cm)
    all_focus_points = list(range(1, 10000))
    
    # get the min, max, and number of focus points from the settings object
    min_focus = settings.get_min_focus()
    max_focus = settings.get_max_focus()
    num_focus_points = settings.get_num_focus_points()

    if num_focus_points == 1:
        return [min_focus]
    elif num_focus_points == 2:
        return [min_focus, max_focus]

    # remove the focus points that are outside the min and max range from all_focus_points
    all_focus_points = [x for x in all_focus_points if x >= min_focus and x <= max_focus]

    focus_points = []
    # add the min focus point to the list 
    focus_points.append(min_focus)

    # get num_focus_points-2 equally spaced points in all_focus_points and add them to the list
    for i in range(1, num_focus_points-1):
        focus_points.append(all_focus_points[i*len(all_focus_points)//(num_focus_points-1)])

    # add the max focus point to the list
    focus_points.append(max_focus)

    return focus_points

def generate_zoom_points(settings: SettingsModel, lem: LensEncoderModel):
    '''
    Generate zoom points for the calibration image gathering process.
    @param settings: CalibrationSettings object
    @param lem: LensEncoderMap object
    '''

    if settings.get_is_prime():
        return [settings.get_prime_zoom()]
    else:
        # generate a list of integers from 1 to 100 (cm)
        all_zoom_points = list(range(1, 1000))

        # get the min, max, and number of zoom points from the settings object
        min_zoom = settings.get_min_zoom()
        max_zoom = settings.get_max_zoom()
        num_zoom_points = settings.get_num_zoom_points()

        if num_zoom_points == 1:
            return [min_zoom]
        elif num_zoom_points == 2:
            return [min_zoom, max_zoom]

        # remove the zoom points that are outside the min and max range from all_zoom_points
        all_zoom_points = [x for x in all_zoom_points if x >= min_zoom and x <= max_zoom]

        zoom_points = []
        # add the min zoom point to the list 
        zoom_points.append(min_zoom)

        # get num_zoom_points-2 equally spaced points in all_zoom_points and add them to the list
        for i in range(1, num_zoom_points-1):
            zoom_points.append(all_zoom_points[i*len(all_zoom_points)//(num_zoom_points-1)])

        # add the max zoom point to the list
        zoom_points.append(max_zoom)

        return zoom_points
