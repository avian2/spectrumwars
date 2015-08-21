from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=255)
	code = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.name

class Round(models.Model):
	started = models.DateTimeField(auto_now_add=True)
	nplayers = models.IntegerField()
	testbed = models.CharField(max_length=255)

	state = models.CharField(max_length=255)

class Game(models.Model):
	duration = models.FloatField()
	ran = models.DateTimeField(auto_now_add=True)
	round = models.ForeignKey(Round)

class PlayerResult(models.Model):
	game = models.ForeignKey(Game)
	player = models.ForeignKey(Player)

	transmit_packets = models.IntegerField()
	received_packets = models.IntegerField()

	payload_bytes = models.IntegerField()

	crashed = models.BooleanField()
	log = models.TextField()
	timeline = models.FileField(upload_to="timeline")

	def get_packet_loss(self):

		if self.transmit_packets > 0.:
			return 100. * (self.transmit_packets - self.received_packets) / self.transmit_packets
		else:
			return float("NaN")

	def get_throughput(self):

		duration = self.game.duration
		if duration > 0.:
			return self.payload_bytes / duration
		else:
			return float("NaN")
