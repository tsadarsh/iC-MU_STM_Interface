import dearpygui.dearpygui as dpg
import time
from enum import Enum
import numpy as np
import threading
from collections import deque


class NumericSingleValueWindow:
    """A general window that displays a single value with a min and max
    """
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.min_value = 0
        self.max_value = 0
        with dpg.window(label=self.name):
            dpg.add_text(default_value=str(self.value), tag=self.name + "_value")
            dpg.add_text(default_value=str(self.value), tag=self.name + "_value_max")
            dpg.add_text(default_value=str(self.value), tag=self.name + "_value_min")

    def update_data(self, value):
        if type(value) == list:
            self.value = float(value[0])
        else:
            self.value = float(value)
        if self.value > self.max_value:
            self.max_value = self.value
        if self.value < self.min_value:
            self.min_value = self.value
        dpg.set_value(item=self.name+"value", value=str(self.value))
        dpg.set_value(item=self.name+"value_max", value="Max: " + str(self.max_value))
        dpg.set_value(item=self.name+"value_min", value="Min: " + str(self.min_value))

    def reset_min_max(self):
        self.min_value = 0
        self.max_value = 0

class TimeSeriesData:

    def __init__(self, labels):
        self.time_data = []
        self.data = [[] for _ in range(len(labels))]
        self.average_sample_time = 1
        self.data_fps = 0

        self.MAX_NUM_SAMPLES = 20000

        self.max_len_thread = threading.Thread(target=self.max_len_t, daemon=True).start()

    def max_len_t(self):
        """a thread used to monitor the maximum length of data and trim it if it
        is getting to long.
        #TODO: replace with a deque
        """
        while 1:
            if len(self.time_data) > self.MAX_NUM_SAMPLES:
                print("Cleaning")
                self.time_data = self.time_data[-self.MAX_NUM_SAMPLES:]
                for i in range(len(self.data)):
                    self.data[i] = self.data[i][-self.MAX_NUM_SAMPLES:]
            time.sleep(1)

    def update_average_sample_time(self, num_sample_received):
        """calculate the average sample time, used for fps calculations and
        dynamic binning.

        Args:
            num_sample_received (_type_): _description_
        """
        if len(self.time_data) == 0:
            return
        self.average_sample_time = (time.time() - self.time_data[-1]) / num_sample_received
        if self.average_sample_time <= 0.000001:
            self.average_sample_time = 0.000001
        self.data_fps = 1.0 / self.average_sample_time

    def update_data(self, values):
        try:
            arrival_time = time.time()
            self.update_average_sample_time(len(values[0]))
            for idx, i in enumerate(values):
                self.data[idx].extend(i)
            
            for i in range(0, len(values[0])):
                self.time_data.append(arrival_time)
        except Exception as e:
            print (e, values)
        
class TimeSeriesWindow:
    """This window is the full featured time series window
    - can provide an FFT and a waterfall plot
    - provides all data in reference to 0
    """

    def __init__(self, name, labels):
        self.name = name
        self.data = TimeSeriesData(labels)
        self.labels = labels
        self.fft_cbs = []
        self.fft_window = FFTWindow(self.name + "_fft", self.labels, self.data)
        self.time_scale = 5.0

        self.maintance_t = threading.Thread(target=self.maintance_thread)
        self.maintance_t.daemon = True
        self.maintance_t.start()

        self.update_window_t = threading.Thread(target=self.update_window_thread)
        self.update_window_t.daemon = True
        self.update_window_t.start()

        self.fft_enabled = False
        self.auto_scale_enabled = True

        self.paused = False

        with dpg.window(label=self.name, tag=self.name+'_win',width=400, height=400):
            dpg.add_text(default_value="FPS: ", tag=self.name + "_fps_label")
            dpg.add_checkbox(label="Enable FFT", callback=self.enable_fft)
            dpg.add_checkbox(label="Autoscale", default_value=True, callback=self.auto_scale)
            dpg.add_input_text(tag=self.name + "_bin_size", label="Bin_Size", default_value="100", callback=self.set_bin_size_cb)
            with dpg.plot(tag=self.name+ '_t_plot', width=-1, height=-1):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="time", tag=self.name+'_x_axis')
                dpg.add_plot_axis(dpg.mvYAxis, label="data", tag=self.name+'_y_axis')
                for label in self.labels:
                    dpg.add_line_series(label=label, x=[], y=[], parent=self.name +'_y_axis', tag=self.name + "_series_" +label)
    
    def set_pause(self, paused):
        """implements the pause functionality for this window
        #TODO: implement a pass to the FFT window

        Args:
            paused (_type_): _description_
        """
        self.paused = paused
    
    def set_bin_size_cb(self, sender, data):
        """callback for when the user changes bin size on the FFT data

        Args:
            sender (_type_): _description_
            data (_type_): _description_
        """
        self.fft_window.bin_size = int(data)
        print("Set bin size to ", data)

    def set_time_period(self, time_scale):
        """implements the time scale functionaility for global time scale

        Args:
            time_scale (_type_): _description_
        """
        self.time_scale = float(time_scale)

    def auto_scale(self, sender, data):
        """callback for setting the plots to autoscale

        Args:
            sender (_type_): _description_
            data (_type_): True if autoscale is eabled
        """
        self.auto_scale_enabled = data
        self.fft_window.set_auto_scale(data)

    def update_window_thread(self):
        """Thread used to update the window
        - this is done so that the window is not updated at the same rate that the
        data is coming in
        """
        while 1:
            time.sleep(1.0/30)
            if self.paused:
                continue
            self.update_plot()
            dpg.set_value(item=self.name + "_fps_label", value="FPS: " + str(int(1.0/self.data.average_sample_time)))

    def maintance_thread(self):
        """A thread with assorted mantainence functions
        """
        while 1:
            time.sleep(0.25)
            self.auto_resize_plots()
    
    def auto_resize_plots(self):
        """resize the plots based on their contents. 
        """
        if self.fft_enabled:
            dpg.set_item_height(self.name + '_t_plot', dpg.get_item_height(self.name + '_win')/2)
        else:
            dpg.set_item_height(self.name + '_t_plot', -1)

    def update_data(self, values):
        self.data.update_data(values)
        #self.update_plot()
        
    def update_plot(self):
        """Preform the functions to select the correct timescale data segment based
        on autoscale and timescale settings
        """
        if self.auto_scale_enabled:
            temp_time_data = [x for x in self.data.time_data if x > (time.time() - self.time_scale)]
            temp_time_data = np.array(temp_time_data)
            temp_time_data = temp_time_data - time.time()
            temp_time_data = list(temp_time_data)
            for idx, label in enumerate(self.labels):
                temp_data_data= self.data.data[idx][-len(temp_time_data):]
                dpg.set_value(self.name + "_series_" +label, value=[list(temp_time_data), list(temp_data_data)])
        else:
            temp_time_data = np.array(self.data.time_data)
            temp_time_data = temp_time_data - time.time()
            temp_time_data = list(temp_time_data)
            for idx, label in enumerate(self.labels):
                dpg.set_value(self.name + "_series_" +label, value=[temp_time_data, self.data.data[idx]])
        if self.auto_scale_enabled:
            dpg.fit_axis_data(self.name + '_x_axis')
            dpg.fit_axis_data(self.name + '_y_axis')

    def enable_fft(self, sender, data):
        """Enable the FFT window or delete the FFT window.
        """
        if data == True:
            self.fft_enabled = True
            self.fft_window.setup_plot()
        else:
            self.fft_enabled = False
            self.fft_window.disable_plot()

class FFTWindow:
    """An FFT viewport/window meant to be contained in a series plot.
    - it inherits its data from a series plot
    - preforms waterfall
    """
    def __init__(self, name, labels, data):
        self.name = name
        self.data = data
        self._bin_size = int(100)
        self.is_enabled = False
        self.labels = labels
        self.auto_scale_enabled = True
        self.fft_update_rate = 2
        self.fft_data = [[[],[]] for _ in range(len(labels))]

        self.fft_thread = threading.Thread(target=self.solve_fft_t)
        self.fft_thread.daemon = True
        self.fft_thread.start()

        self.waterfall_height = 100
        self.waterfall_width = 400
        self.waterfall_texture = deque(maxlen=self.waterfall_height * self.waterfall_width * 4)

        self.update_window_t = threading.Thread(target=self.update_window_thread)
        self.update_window_t.daemon = True
        self.update_window_t.start()

        for i in range(0, self.waterfall_height * self.waterfall_width * 4):
            self.waterfall_texture.append(15)

        self.peaks = [[[],[]] for _ in range(len(labels))]

    def disable_plot(self):
        """deletes the window objects
        TODO: check that other processes are also stopped
        """
        if self.is_enabled:
            dpg.delete_item(self.name + '_t_fft_plot', children_only=True)
            self.is_enabled = False

    def update_window_thread(self):
        while 1:
            time.sleep(1.0/60)
            self.update_plot()

    def get_rgb(self, value, minimum, maximum):
        ratio = 2 * (value-minimum) / (maximum - minimum)
        b = int(max(0, 255*(1 - ratio)))
        r = int(max(0, 255*(ratio - 1)))
        g = 255 - b - r
        return (r, g, b)


    def update_water_fall(self, fft_data):
        new_array = np.interp(np.linspace(0, len(fft_data) - 1, self.waterfall_width), np.arange(len(fft_data)), fft_data)
        new_array = np.clip(new_array, a_min=None, a_max=50)
        new_array = (new_array/50.0*255).astype(np.uint8)
        new_array[new_array < 20] = 0
        for i in range(0, len(new_array)):
            r,g,b = self.get_rgb(new_array[i], 0, 255)
            self.waterfall_texture.append(r)
            self.waterfall_texture.append(0)
            self.waterfall_texture.append(g)
            self.waterfall_texture.append(b)
        dpg.set_value(self.name + "texture_tag", list(self.waterfall_texture))

    def setup_plot(self):
        
        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(width=self.waterfall_width, height=self.waterfall_height , default_value=list(self.waterfall_texture), tag=self.name + "texture_tag")

        dpg.add_image(self.name + "texture_tag", parent=self.name.split('_')[0] + "_win")
        
        with dpg.plot(tag=self.name+ '_t_fft_plot', width=-1, height=-1, parent=self.name.split('_')[0] + "_win"):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="freq", tag=self.name+'_x_axis_fft')
            dpg.add_plot_axis(dpg.mvYAxis, label="amp", tag=self.name+'_y_axis_fft')
            for label in self.labels:
                dpg.add_line_series(label=label + "_fft", x=[], y=[], parent=self.name+'_y_axis_fft', tag=self.name + "_fft_series_" +label)
                #dpg.add_scatter_series([], [], label="FFT Peaks", parent=self.name+'_y_axis', tag=self.name + "_fft_peaks_series"+label)

        self.is_enabled = True
    
    def set_auto_scale(self, auto_scale):
        self.auto_scale_enabled = auto_scale

    @property
    def bin_size(self):
        return self._bin_size

    @bin_size.setter
    def bin_size(self, value):
        self._bin_size = int(value)#int(value)


    def detect_peaks(self, arr, threshold):

        peak_indices = []
        prev_peak_idx = -threshold

        for i in range(1, len(arr)-1):
            if arr[i] > arr[i-1] and arr[i] > arr[i+1]:
                if i - prev_peak_idx > threshold:
                    if (i > threshold/2.0):
                        peak_indices.append(i)
                        prev_peak_idx = i
        peak_x = []
        peak_y = []
        for idx in peak_indices:
            peak_x.append(self.fft_data[0][0][idx])
            peak_y.append(self.fft_data[0][1][idx])
        return peak_x, peak_y


    def solve_fft_t(self):
        over_sample = 4
        while 1:
            tmp_bin_size = self._bin_size * over_sample
            try:
                time.sleep(1.0/self.fft_update_rate)
                if len(self.data.time_data) < ((tmp_bin_size) + 1):
                    continue
                if self.is_enabled == False:
                    continue
                for i in range(0, len(self.fft_data)):
                    sp = np.abs(np.fft.fft(self.data.data[i][-tmp_bin_size:]).real)
                    freq = np.fft.fftfreq(tmp_bin_size, d=over_sample/tmp_bin_size)
                    sp[0] = 0
                    sp[1] = 0
                    sp[2] = 0
                    self.fft_data[i][0] = (freq[:int(tmp_bin_size/4)])
                    self.fft_data[i][1] = (sp[:int(tmp_bin_size/4)])
                    #self.fft_data[i][1] = (max(self.data.data[i]) * sp[:int(self._bin_size/2)] / max(abs(sp[:int(self._bin_size/2)])))
                    #self.peaks[i] = self.detect_peaks(self.fft_data[i][1], max(self.data.data[i])/2.0)
            except Exception as e:
                print(e)
                pass
            self.update_water_fall(self.fft_data[2][1])

    def update_plot(self):
        if not self.is_enabled:
            return
        for idx, label in enumerate(self.labels):
            dpg.set_value(self.name + "_fft_series_" +label, value=[list(self.fft_data[idx][0]), list(self.fft_data[idx][1])])
            #dpg.set_value(self.name + "_fft_peaks_series"+label, value=self.peaks[idx])
        # if self.auto_scale_enabled:
        #     dpg.fit_axis_data(self.name + '_x_axis_fft')
        #     dpg.fit_axis_data(self.name + '_y_axis_fft')