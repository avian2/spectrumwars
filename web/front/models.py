from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=255)
	code = models.TextField()

	def __unicode__(self):
		return self.name

class Game(models.Model):
	pass

class PlayerResult(models.Model):
	game = models.ForeignKey(Game)
	player = models.ForeignKey(Player)
	received_ratio = models.FloatField()
	crashed = models.BooleanField()
	log = models.TextField()
	timeline = models.FileField(upload_to="timeline")
