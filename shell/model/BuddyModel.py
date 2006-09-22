from sugar.presence import PresenceService
from sugar.canvas.IconColor import IconColor

class BuddyModel:
	def __init__(self, name=None, buddy=None):
		if name and buddy:
			raise RuntimeError("Must specify only _one_ of name or buddy.")

		self._cur_activity = None
		self._buddy_appeared_handler = None
		self._pservice = PresenceService.get_instance()

		self._buddy = buddy

		# If given just a name, try to get the buddy from the PS first
		if not self._buddy:
			self._name = name
			# FIXME: use public key, not name
			self._buddy = self._pservice.get_buddy_by_name(self._name)

		# If successful, copy properties from the PS buddy object
		if self._buddy:
			self.__update_buddy(buddy)
		else:
			# Otherwise, connect to the PS's buddy-appeared signal and
			# wait for the buddy to appear
			self._buddy_appeared_handler = self._pservice.connect('buddy-appeared',
					self.__buddy_appeared_cb)
			self._name = name
			# Set color to 'inactive'/'disconnected'
			self.__set_color_from_string("#888888,#BBBBBB")

	def __set_color_from_string(self, color_string):
		self._color = IconColor(color_string)

	def get_name(self):
		return self._name

	def get_color(self):
		return self._color

	def get_buddy(self):
		return self._buddy

	def __update_buddy(self, buddy):
		if not buddy:
			raise ValueError("Buddy cannot be None.")
		self._buddy = buddy
		self._name = self._buddy.get_name()
		self.__set_color_from_string(self._buddy.get_color())
		self._buddy.connect('property-changed', self.__buddy_property_changed_cb)

	def __buddy_appeared_cb(self, pservice, buddy):
		# FIXME: use public key rather than buddy name
		if self._buddy or buddy.get_name() != self._name:
			return

		if self._buddy_appeared_handler:
			# Once we have the buddy, we no longer need to
			# monitor buddy-appeared events
			self._pservice.disconnect(self._buddy_appeared_handler)
			self._buddy_appeared_handler = None

		self.__update_buddy(buddy)

	def __buddy_property_changed_cb(self, buddy, keys):
		# all we care about right now is current activity
		curact = self._buddy.get_current_activity()
		self._cur_activity = self._pservice.get_activity(curact)

