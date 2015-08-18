from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=255)
	code = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.name

class Game(models.Model):
	duration = models.FloatField()
	ran = models.DateTimeField(auto_now_add=True)

class PlayerResult(models.Model):
	game = models.ForeignKey(Game)
	player = models.ForeignKey(Player)

	transmit_packets = models.IntegerField()
	received_packets = models.IntegerField()

	payload_bytes = models.IntegerField()

	received_ratio = models.FloatField()

	crashed = models.BooleanField()
	log = models.TextField()
	timeline = models.FileField(upload_to="timeline")
