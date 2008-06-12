from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from music import settings
from django.contrib.auth.models import User
from tagging.fields import TagField
from published_manager.managers import PublishedManager
from django.template.defaultfilters import slugify
from music.audioscrobbler import AudioScrobblerQuery

class LastFmUser(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"), null=True, blank=True)
    lastfm_id = models.CharField(max_length=50, verbose_name=_("Last Fm Id"))

    class Admin:
        pass

    def __unicode__(self):
        return _("%s %s" % (self.user.__unicode__(), self.lastfm_id))

    def sync_tracks(self):
        q = AudioScrobblerQuery(user=self.lastfm_id)
        r = q.recenttracks()
        tracks = [dict([(d.tag, d.text) for d in t]) for t in r]
        for track in tracks:
            try:
                row = Track.objects.get(title=track['name'], artist=track['artist'], lastfm_user=self)
            except ObjectDoesNotExist:
                t = Track(title=track['name'], artist=track['artist'], slug=slugify(track['name']), lastfm_user=self)
                t.save()

class Track(models.Model):
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Published"))
    lastfm_user = models.ForeignKey(LastFmUser, verbose_name=_("LastFm User"))
    state = models.CharField(max_length=1, choices=settings.STATE_CHOICES, default=settings.STATE_DEFAULT, verbose_name=_("State of object"))
    ip_address = models.IPAddressField(verbose_name=_("Author's IP Address"), null=True, blank=True)
    tags = TagField(help_text=_("Enter key terms seperated with a space that you want to associate with this Entry"), verbose_name=_("Tags"))
    slug = models.SlugField(prepopulate_from=('title',), unique=True, verbose_name=_("Slug Field"))
    published_objects = PublishedManager()
    objects = models.Manager()

    class Admin:
        pass

    def __unicode__(self):
        return _("%s by %s" % (self.title, self.artist))
