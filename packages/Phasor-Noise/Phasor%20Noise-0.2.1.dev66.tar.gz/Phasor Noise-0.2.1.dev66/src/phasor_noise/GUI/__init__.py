import phasor_noise.GUI.menu as menu
import phasor_noise.generator as generator
import phasor_noise.analysis as analysis
import tkinter as tk
import random as rd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageTk
import json
from skimage import exposure
from copy import deepcopy
from phasor_noise.GUI.directory import *
import os


class Window:
    """
    Window GUI to manipulate the phasor noise and analyse it
    """
    def __init__(self, master, version="Python") -> None:
        """
        Initialization of the window with default configuration
        Load a 1090x720 window with the homepage
        """
        self.master = master
        self.visualize = tk.BooleanVar()
        self.master.resizable(height=False, width=False)
        self.master.title("Générateur de bruit Phasor - Version : " + version)
        self.master.geometry("1090x720")
        self.currentPage = 0
        self.gen_mode = version
        self.load_page()
        self.menu = menu.Menu(self)

    def save(self):
        """
        Save current configuration
        """
        new_config = {
            "x": self.img_size_x.get(),
            "y": self.img_size_y.get(),
            "nb_ker": self.img_nb_ker.get(),
            "min_freq": self.img_freq_min.get(),
            "max_freq": self.img_freq_max.get(),
            "min_angle": self.img_angle_min.get(),
            "max_angle": self.img_angle_max.get(),
            "min_bandwidth": self.img_bandwidth_min.get(),
            "max_bandwidth": self.img_bandwidth_max.get()
        }
        config_file = open(f"{config_directory}/config.json", 'w')
        json.dump(new_config, config_file)

    def reload(self):
        """
        Reload the page
        """
        self.page.destroy()
        path = f"{config_directory}/config.json"
        if os.path.exists(path):
            config_file = open(f"{config_directory}/config.json", "r")
            config = json.load(config_file)
        else:
            config_file = open(f"{config_directory}/config.json", "w")
            config = {"x": "100", "y": "100", "nb_ker": "10", "min_freq": "1", "max_freq": "1", "min_angle": "-1.57",
                      "max_angle": "1.57", "min_bandwidth": "0.1", "max_bandwidth": "0.1"}
            json.dump(config, config_file)
        self.config = config
        self.load_page()

    def load_page(self):
        """
        Load page
        """
        if self.currentPage == 0:
            self.page = tk.Frame(self.master)
            self.title = tk.Label(self.page, text=f"Générateur de bruit Phasor - {self.gen_mode}", font=("Times", 25))
            self.title.grid(row=0, column=0, columnspan=2, pady=(20, 20))

            self.one_image_button = tk.Button(self.page, text="Analyse d'un unique bruit", command=self.one_noise_mode)
            self.one_image_button.grid(row=1, column=0, ipady=50, pady=(200, 50))

            self.multi_test_button = tk.Button(self.page, text="Test de performances", command=self.test_performance)
            self.multi_test_button.grid(row=1, column=1, ipady=50, pady=(200, 50))

            self.page.pack()
        elif self.currentPage == 1:
            self.page = tk.Frame(self.master)
            self.title = tk.Label(self.page, text=f"Analyse d'un unique bruit - {self.gen_mode}", font=("Times", 20))
            self.title.grid(row=0, column=0, columnspan=2, pady=(20, 70))

            self.visu_img = tk.Canvas(self.page, bg='white', height=500, width=500)
            self.visu_img.grid(row=1, column=0, rowspan=2, padx=10, sticky="nswe")

            self.config_img = tk.Frame(self.page, relief=tk.GROOVE, bd=3)
            self.config_img_title = tk.Label(self.config_img, text=f"Configuration du bruit", font=("Times", 15))
            self.config_img_title.grid(row=0, column=0, columnspan=4, ipady=10)

            self.img_size_title = tk.Label(self.config_img, text=f"Taille de l'image :")
            self.img_size_title.grid(row=1, column=0)
            self.img_size_x = tk.Entry(self.config_img)
            self.img_size_x.insert(0, str(self.config["x"]))
            self.img_size_x.grid(row=1, column=1)
            self.img_size_label1 = tk.Label(self.config_img, text=f" x ")
            self.img_size_label1.grid(row=1, column=2)
            self.img_size_y = tk.Entry(self.config_img)
            self.img_size_y.insert(0, str(self.config["y"]))
            self.img_size_y.grid(row=1, column=3)

            self.img_nb_ker_title = tk.Label(self.config_img, text=f"Nombre de noyaux :")
            self.img_nb_ker_title.grid(row=2, column=0)
            self.img_nb_ker = tk.Entry(self.config_img)
            self.img_nb_ker.insert(0, str(self.config["nb_ker"]))
            self.img_nb_ker.grid(row=2, column=1)

            self.img_freq_title = tk.Label(self.config_img, text=f"Fréquences :")
            self.img_freq_title.grid(row=3, column=0)
            self.img_freq_min = tk.Entry(self.config_img)
            self.img_freq_min.insert(0, str(self.config["min_freq"]))
            self.img_freq_min.grid(row=3, column=1)
            self.img_freq_label = tk.Label(self.config_img, text=f" < f < ")
            self.img_freq_label.grid(row=3, column=2)
            self.img_freq_max = tk.Entry(self.config_img)
            self.img_freq_max.insert(0, str(self.config["max_freq"]))
            self.img_freq_max.grid(row=3, column=3)

            self.img_angle_title = tk.Label(self.config_img, text=f"Angles :")
            self.img_angle_title.grid(row=4, column=0)
            self.img_angle_min = tk.Entry(self.config_img)
            self.img_angle_min.insert(0, str(self.config["min_angle"]))
            self.img_angle_min.grid(row=4, column=1)
            self.img_angle_label = tk.Label(self.config_img, text=f" < a < ")
            self.img_angle_label.grid(row=4, column=2)
            self.img_angle_max = tk.Entry(self.config_img)
            self.img_angle_max.insert(0, str(self.config["max_angle"]))
            self.img_angle_max.grid(row=4, column=3)

            self.img_bandwidth_title = tk.Label(self.config_img, text=f"Bandes :")
            self.img_bandwidth_title.grid(row=5, column=0)
            self.img_bandwidth_min = tk.Entry(self.config_img)
            self.img_bandwidth_min.insert(0, str(self.config["min_bandwidth"]))
            self.img_bandwidth_min.grid(row=5, column=1)
            self.img_bandwidth_label = tk.Label(self.config_img, text=f" < b < ")
            self.img_bandwidth_label.grid(row=5, column=2)
            self.img_bandwidth_max = tk.Entry(self.config_img)
            self.img_bandwidth_max.insert(0, str(self.config["max_bandwidth"]))
            self.img_bandwidth_max.grid(row=5, column=3)

            self.img_gen_button = tk.Button(self.config_img, text="Générer", command=self.validate_entry)
            self.img_gen_button.grid(row=6, column=0, columnspan=4, pady=(20, 0))

            self.config_img.grid(row=1, column=1, ipadx=10, ipady=10, sticky="nwe", pady=(00, 0))

            self.console_img = tk.Frame(self.page, relief=tk.GROOVE, bd=3)

            self.console_img_title = tk.Label(self.console_img, text=f"Console", font=("Times", 15))
            self.console_img_title.grid(row=0, column=0, ipadx=50, pady=(10, 0), sticky="w")

            self.console_text = tk.StringVar()
            self.console_text.set("En attente...")
            self.console_label = tk.Label(self.console_img, textvariable=self.console_text, justify="left")
            self.console_label.grid(row=1, column=0, sticky="w")
            self.console_img.grid(row=2, column=1, sticky="nswe")

            self.return_button = tk.Button(self.page, text="Retour", command=self.return_menu)
            self.return_button.grid(row=3, column=1, pady=50, sticky="e")

            self.button_chooser = tk.Frame(self.page, relief=tk.GROOVE, bd=3)
            self.img_button = tk.Button(self.button_chooser, text="Image", command=self.visu_mode_img)
            self.img_button.grid(column=0, row=0)
            self.histo_button = tk.Button(self.button_chooser, text="Histogramme", command=self.visu_mode_hist)
            self.histo_button.grid(column=1, row=0)
            self.psd_button = tk.Button(self.button_chooser, text="Densité spect. de puissance",
                                        command=self.visu_mode_psd)
            self.psd_button.grid(column=2, row=0)

            self.button_chooser.grid(row=3, column=0, sticky="n")

            self.page.pack()

        elif self.currentPage == 2:
            self.page = tk.Frame(self.master)
            self.title = tk.Label(self.page, text=f"Test de performances", font=("Times", 20))
            self.title.grid(row=0, column=0, columnspan=2, pady=(20, 70))

            self.visu_img = tk.Canvas(self.page, bg='white', height=500, width=500)
            self.visu_img.grid(row=1, column=0, rowspan=2, padx=10, sticky="nswe")

            self.config_img = tk.Frame(self.page, relief=tk.GROOVE, bd=3)
            self.config_img_title = tk.Label(self.config_img, text=f"Configuration des bruits", font=("Times", 15))
            self.config_img_title.grid(row=0, column=0, columnspan=4, ipady=10)

            self.img_size_title = tk.Label(self.config_img, text=f"Taille des images :")
            self.img_size_title.grid(row=1, column=0)
            self.img_size_x = tk.Entry(self.config_img)
            self.img_size_x.insert(0, str(self.config["x"]))
            self.img_size_x.grid(row=1, column=1)
            self.img_size_label1 = tk.Label(self.config_img, text=f" x ")
            self.img_size_label1.grid(row=1, column=2)
            self.img_size_y = tk.Entry(self.config_img)
            self.img_size_y.insert(0, str(self.config["y"]))
            self.img_size_y.grid(row=1, column=3)

            self.img_nb_ker_title = tk.Label(self.config_img, text=f"Nombre de noyaux :")
            self.img_nb_ker_title.grid(row=2, column=0)
            self.img_nb_ker = tk.Entry(self.config_img)
            self.img_nb_ker.insert(0, str(self.config["nb_ker"]))
            self.img_nb_ker.grid(row=2, column=1)

            self.img_freq_title = tk.Label(self.config_img, text=f"Fréquences :")
            self.img_freq_title.grid(row=3, column=0)
            self.img_freq_min = tk.Entry(self.config_img)
            self.img_freq_min.insert(0, str(self.config["min_freq"]))
            self.img_freq_min.grid(row=3, column=1)
            self.img_freq_label = tk.Label(self.config_img, text=f" < f < ")
            self.img_freq_label.grid(row=3, column=2)
            self.img_freq_max = tk.Entry(self.config_img)
            self.img_freq_max.insert(0, str(self.config["max_freq"]))
            self.img_freq_max.grid(row=3, column=3)

            self.img_angle_title = tk.Label(self.config_img, text=f"Angles :")
            self.img_angle_title.grid(row=4, column=0)
            self.img_angle_min = tk.Entry(self.config_img)
            self.img_angle_min.insert(0, str(self.config["min_angle"]))
            self.img_angle_min.grid(row=4, column=1)
            self.img_angle_label = tk.Label(self.config_img, text=f" < a < ")
            self.img_angle_label.grid(row=4, column=2)
            self.img_angle_max = tk.Entry(self.config_img)
            self.img_angle_max.insert(0, str(self.config["max_angle"]))
            self.img_angle_max.grid(row=4, column=3)

            self.img_bandwidth_title = tk.Label(self.config_img, text=f"Bandes :")
            self.img_bandwidth_title.grid(row=5, column=0)
            self.img_bandwidth_min = tk.Entry(self.config_img)
            self.img_bandwidth_min.insert(0, str(self.config["min_bandwidth"]))
            self.img_bandwidth_min.grid(row=5, column=1)
            self.img_bandwidth_label = tk.Label(self.config_img, text=f" < b < ")
            self.img_bandwidth_label.grid(row=5, column=2)
            self.img_bandwidth_max = tk.Entry(self.config_img)
            self.img_bandwidth_max.insert(0, str(self.config["max_bandwidth"]))
            self.img_bandwidth_max.grid(row=5, column=3)
            self.number_label = tk.Label(self.config_img, text=f"Occurences :")
            self.number_label.grid(row=6, column=0)
            self.number = tk.Entry(self.config_img)
            self.number.insert(0, str(self.config["max_bandwidth"]))
            self.number.grid(row=6, column=1)

            self.img_gen_button = tk.Button(self.config_img, text="Générer", command=self.validate_entry_performance)
            self.img_gen_button.grid(row=7, column=0, columnspan=4, pady=(20, 0))

            self.config_img.grid(row=1, column=1, ipadx=10, ipady=10, sticky="nwe", pady=(00, 0))

            self.console_img = tk.Frame(self.page, relief=tk.GROOVE, bd=3)

            self.console_img_title = tk.Label(self.console_img, text=f"Console", font=("Times", 15))
            self.console_img_title.grid(row=0, column=0, ipadx=50, pady=(10, 0), sticky="w")

            self.console_text = tk.StringVar()
            self.console_text.set("En attente...")
            self.console_label = tk.Label(self.console_img, textvariable=self.console_text, justify="left")
            self.console_label.grid(row=1, column=0, sticky="w")
            self.console_img.grid(row=2, column=1, sticky="nswe")

            self.return_button = tk.Button(self.page, text="Retour", command=self.return_menu)
            self.return_button.grid(row=3, column=1, pady=50, sticky="e")

            self.page.pack()

        else:
            print("error")

    def visu_mode_img(self):
        """
        Show image
        """
        try:
            self.visu_img.delete(self.noise)
        except:
            pass
        try:
            img = Image.open(f"{images_directory}/noise.png")
            img.thumbnail((500, 500), Image.ANTIALIAS)
            img.save(f"{images_directory}/noise_reshape.png")
            self.img = ImageTk.PhotoImage(Image.open(f"{images_directory}/noise_reshape.png"))
            self.noise = self.visu_img.create_image(0, 0, image=self.img, anchor="nw", tags="IMG")
        except:
            self.console_text.set("Générer d'abord un nouveau bruit !")

    def visu_mode_psd(self):
        """
        Show power spectral density
        """
        try:
            self.visu_img.delete(self.noise)
        except:
            pass
        try:
            img = Image.open(f"{images_directory}/noise_psd.png")
            img.thumbnail((500, 500), Image.ANTIALIAS)
            img.save(f"{images_directory}/noise_psd_reshape.png")
            self.img = ImageTk.PhotoImage(Image.open(f"{images_directory}/noise_psd_reshape.png"))
            self.noise = self.visu_img.create_image(0, 0, image=self.img, anchor="nw", tags="IMG")
        except:
            self.console_text.set("Générer d'abord un nouveau bruit !")

    def visu_mode_hist(self):
        """
        Show histogram
        """
        try:
            self.visu_img.delete(self.noise)
        except:
            pass
        try:
            img = Image.open(f"{images_directory}/noise_hist.png")
            img.thumbnail((500, 500), Image.ANTIALIAS)
            img.save(f"{images_directory}/noise_hist_reshape.png")
            self.img = ImageTk.PhotoImage(Image.open(f"{images_directory}/noise_hist_reshape.png"))
            self.noise = self.visu_img.create_image(0, 0, image=self.img, anchor="nw", tags="IMG")
        except:
            self.console_text.set("Générer d'abord un nouveau bruit !")

    def return_menu(self):
        """
        Menu
        """
        self.currentPage = 0
        self.reload()

    def validate_entry(self):
        """
        Parsing entry values
        """
        try:
            x = int(self.img_size_x.get())
            y = int(self.img_size_x.get())
            nb_ker = int(self.img_nb_ker.get())
            freq_min = float(self.img_freq_min.get())
            freq_max = float(self.img_freq_max.get())
            angle_min = float(self.img_angle_min.get())
            angle_max = float(self.img_angle_max.get())
            bandwidth_min = float(self.img_bandwidth_min.get())
            bandwidth_max = float(self.img_bandwidth_max.get())
            self.console_text.set("Génération du bruit...")

        except:
            self.console_text.set("Une erreur est survenu vérifier les valeurs entrées...")

        self.gen_kernels([x, y], nb_ker, [freq_min, freq_max], [angle_min, angle_max], [bandwidth_min, bandwidth_max])
        self.gen_noise()

    def validate_entry_performance(self):
        """
        Parsing entry performances values
        """
        try:
            n = int(self.number.get())
            x = int(self.img_size_x.get())
            y = int(self.img_size_x.get())
            nb_ker = int(self.img_nb_ker.get())
            freq_min = float(self.img_freq_min.get())
            freq_max = float(self.img_freq_max.get())
            angle_min = float(self.img_angle_min.get())
            angle_max = float(self.img_angle_max.get())
            bandwidth_min = float(self.img_bandwidth_min.get())
            bandwidth_max = float(self.img_bandwidth_max.get())
            self.console_text.set("Génération du bruit...")

        except:
            self.console_text.set("Une erreur est survenu vérifier les valeurs entrées...")

        self.gen_kernels([x, y], nb_ker, [freq_min, freq_max], [angle_min, angle_max], [bandwidth_min, bandwidth_max])
        self.gen_noise()

    def gen_kernels(self, size, nb_ker, freq, angle, bandwidth):
        """
        Generation of a kernel
        """
        self.size = size
        kernels = list()
        for i in range(nb_ker):
            pos = [rd.randint(0, size[0]), rd.randint(0, size[1])]
            ang = rd.uniform(angle[0], angle[1])
            dire = [np.cos(ang), np.sin(ang)]
            f = rd.uniform(freq[0], freq[1])
            b = rd.uniform(bandwidth[0], bandwidth[1])
            kernels.append([pos, dire, f, b])
        self.kernels = kernels

    def gen_noise(self):
        if self.gen_mode == "Python":
            X = np.arange(0, self.size[0])
            Y = np.arange(0, self.size[1])
            X, Y = np.meshgrid(X, Y)
            self.results = generator.apply_noise_python(X, Y, self.kernels)
            plt.contourf(X, Y, self.results[0], cmap='Greys')
            plt.colorbar()
            plt.axis('off')
            if self.visualize.get() == 1:
                for kernel in self.kernels:
                    plt.plot(kernel[0][0], kernel[0][1], color="green", marker="o")
                    plt.arrow(kernel[0][0], kernel[0][1], kernel[1][0] * 5, kernel[1][1] * 5, width=1, head_width=2,
                              head_length=2, color="red")
            mean = analysis.mean(self.results[0])
            std_gap = analysis.std_gap(self.results[0])
            self.console_text.set(
                f"Le bruit à bien été créé en {self.results[1] / 10 ** 6} ms ! \n Moyenne: {mean} \n Ecart-type: {std_gap}")
            plt.savefig(f"{images_directory}/noise.png", bbox_inches='tight')
            plt.close()

            mag = analysis.PSD(np.array(self.results[0]))
            plt.contourf(X, Y, mag, cmap="Greys_r")
            plt.axis('off')
            plt.colorbar()
            plt.savefig(f"{images_directory}/noise_psd.png", bbox_inches='tight')
            plt.close()

            hist = exposure.histogram(np.array(self.results[0]))
            plt.plot(hist[1], hist[0])

            plt.savefig(f"{images_directory}/noise_hist.png", bbox_inches='tight')
            self.visu_mode_img()

            plt.savefig(f"{images_directory}/noise_hist.png", bbox_inches='tight')
            self.visu_mode_img()

        elif self.gen_mode == "Numpy":
            X = np.arange(0, self.size[0])
            Y = np.arange(0, self.size[1])
            X, Y = np.meshgrid(X, Y)
            self.results = generator.apply_noise_numpy(X, Y, deepcopy(self.kernels),
                                                                                 self.size)
            plt.contourf(X, Y, self.results[0], cmap='Greys')
            plt.axis('off')
            plt.colorbar()
            if self.visualize.get() == 1:
                for kernel in self.kernels:
                    plt.plot(kernel[0][0], kernel[0][1], color="green", marker="o")
                    plt.arrow(kernel[0][0], kernel[0][1], kernel[1][0] * 5, kernel[1][1] * 5, width=1, head_width=2,
                              head_length=2, color="red")
            mean = analysis.mean(self.results[0])
            std_gap = analysis.std_gap(self.results[0])
            self.console_text.set(
                f"Le bruit à bien été créé en {self.results[1] / 10 ** 6} ms !\n Moyenne: {mean}\nEcart-type: {std_gap}")
            plt.savefig(f"{images_directory}/noise.png", bbox_inches='tight')
            plt.close()

            mag = analysis.PSD(np.array(self.results[0]))
            plt.contourf(X, Y, mag, cmap='Greys')
            plt.axis('off')
            plt.colorbar()
            plt.savefig(f"{images_directory}/noise_psd.png", bbox_inches='tight')
            plt.close()

            hist = exposure.histogram(np.array(self.results[0]))
            plt.plot(hist[1], hist[0])

            plt.savefig(f"{images_directory}/noise_hist.png", bbox_inches='tight')
            self.visu_mode_img()

        plt.close()

    def one_noise_mode(self):
        """
        One noise mode
        """
        self.currentPage = 1
        self.reload()

    def test_performance(self):
        """
        Testing performance
        """
        self.currentPage = 2
        self.reload()

    def change_mode_python(self):
        """
        Set to builtins Python calculation
        """
        self.gen_mode = "Python"
        self.reload()

    def change_mode_numpy(self):
        """
        Set to numpy calculation
        """
        self.gen_mode = "Numpy"
        self.reload()

    def change_mode_jax(self):
        """
        Set to Jax calculation
        """
        self.gen_mode = "JAX"
        self.reload()
