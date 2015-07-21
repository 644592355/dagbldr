# Author: Kyle Kastner
# License: BSD 3-clause
import random
import os
import glob
import subprocess
from itertools import cycle


def plot_training_epochs(epochs_dict, plot_name, plot_limit=None, turn_on_agg=True):
    # plot_limit can be a positive integer, negative integer, or float between 0 and 1
    # foat between 0 and 1 assumed to be percentage of total to keep
    if turn_on_agg:
        import matplotlib
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # colors from seaborn flatui
    color_list = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
    colors = cycle(color_list)
    for key in epochs_dict.keys():
        if plot_limit < 1 and plot_limit > 0:
           plot_limit = int(plot_limit * len(epochs_dict[key]))
        plt.plot(epochs_dict[key][:plot_limit], color=colors.next())
        plt.title(str(key))
        plt.savefig(plot_name + "_" + str(key) + ".png")
        plt.close()


def plot_images_as_subplots(list_of_plot_args, plot_name, width, height,
                            invert_y=False, invert_x=False, turn_on_agg=True):
    if turn_on_agg:
        import matplotlib
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    lengths = [len(a) for a in list_of_plot_args]
    if len(list(filter(lambda x: x != lengths[0], lengths))) > 0:
        raise ValueError("list_of_plot_args has elements of different lengths!")

    f, axarr = plt.subplots(lengths[0], len(lengths))
    for n, v in enumerate(list_of_plot_args):
        for i, X_i in enumerate(v):
            axarr[i, n].matshow(X_i.reshape(width, height), cmap="gray", interpolation="none")
            axarr[i, n].axis('off')
            if invert_y:
                axarr[i, n].set_ylim(axarr[i, n].get_ylim()[::-1])
            if invert_x:
                axarr[i, n].set_xlim(axarr[i, n].get_xlim()[::-1])
    plt.savefig(plot_name + ".png")


def make_gif(arr, gif_name, plot_width, plot_height, resize_scale_width=5, resize_scale_height=5,
             list_text_per_frame=None, invert_y=False, invert_x=False,
             list_text_per_frame_color=None,
             delay=1, grayscale=False,
             loop=False, turn_on_agg=True):
    """ Make a gif from a series of pngs using matplotlib matshow """
    if turn_on_agg:
        import matplotlib
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # Plot temporaries for making gif
    # use random code to try and avoid deleting surprise files...
    random_code = random.randrange(2 ** 32)
    pre = str(random_code)
    for n, arr_i in enumerate(arr):
        plt.matshow(arr_i.reshape(plot_width, plot_height), cmap="gray", interpolation="none")
        if invert_y:
            ax = plt.gca()
            ax.set_ylim(ax.get_ylim()[::-1])
        if invert_x:
            ax = plt.gca()
            ax.set_xlim(ax.get_xlim()[::-1])

        plt.axis('off')
        if list_text_per_frame is not None:
            text = list_text_per_frame[n]
            if list_text_per_frame_color is not None:
                color = list_text_per_frame_color[n]
            else:
                color = "white"
            plt.text(0, plot_height, text, color=color,
                     fontsize=2 * plot_height)
        # This looks rediculous but should count the number of digit places
        # also protects against multiple runs
        # plus 1 is to maintain proper ordering
        plotpath = '__%s_giftmp_%s.png' % (str(n).zfill(len(
            str(len(arr))) + 1), pre)
        plt.savefig(plotpath)
        plt.close()

    # make gif
    assert delay >= 1
    gif_delay = int(delay)
    basestr = "convert __*giftmp_%s.png -delay %s " % (pre, str(gif_delay))
    if loop:
        basestr += "-loop 1 "
    else:
        basestr += "-loop 0 "
    if grayscale:
        basestr += "-depth 8 -type Grayscale -depth 8 "
    basestr += "-resize %sx%s " % (str(int(resize_scale_width * plot_width)),
                                   str(int(resize_scale_height * plot_height)))
    basestr += gif_name
    print("Attempting gif")
    print(basestr)
    subprocess.call(basestr, shell=True)
    filelist = glob.glob("__*giftmp_%s.png" % pre)
    for f in filelist:
        os.remove(f)
