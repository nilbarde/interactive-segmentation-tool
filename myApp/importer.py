if True:
	import kivy

	from kivy.app import App

	from kivy.lang import Builder
	from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
	from kivy.uix.button import Button
	from kivy.uix.behaviors import ButtonBehavior
	from kivy.uix.label import Label
	from kivy.uix.checkbox import CheckBox
	from kivy.uix.textinput import TextInput
	from kivy.uix.widget import Widget
	from kivy.uix.dropdown import DropDown
	from kivy.uix.progressbar import ProgressBar
	from kivy.animation import Animation
	from kivy.uix.bubble import Bubble
	from kivy.clock import Clock

	from kivy.uix.gridlayout import GridLayout
	from kivy.uix.boxlayout import BoxLayout
	from kivy.uix.floatlayout import FloatLayout
	from kivy.uix.scrollview import ScrollView
	from kivy.core.window import Window

	from kivy.uix.image import Image
	from kivy.uix.videoplayer import VideoPlayer
	from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle

	from kivy.properties import StringProperty, BooleanProperty, NumericProperty
	from kivy.uix.slider import Slider
	from kivy.uix.popup import Popup
	from kivy.config import Config
	from kivy.cache import Cache
	Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
	
	from functools import partial
	import cv2
	import numpy as np
	from os.path import dirname, basename, exists, isfile
	from os import makedirs
	import imutils
else:
	print("*******************************")
	print("  error in importing packages  ")
	print("*******************************")

class ImageButton(ButtonBehavior, Image):
	pass
