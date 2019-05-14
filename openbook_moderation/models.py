from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from django.utils import timezone

from openbook_auth.models import User


class ModerationCategory(models.Model):
    name = models.CharField(_('name'), max_length=32, blank=False, null=False)
    title = models.CharField(_('title'), max_length=64, blank=False, null=False)
    description = models.CharField(_('description'), max_length=255, blank=False, null=False)
    created = models.DateTimeField(editable=False, db_index=True)

    SEVERITY_CRITICAL = 'C'
    SEVERITY_HIGH = 'H'
    SEVERITY_MEDIUM = 'M'
    SEVERITY_LOW = 'L'
    SEVERITIES = (
        (SEVERITY_CRITICAL, 'Critical'),
        (SEVERITY_HIGH, 'High'),
        (SEVERITY_MEDIUM, 'Medium'),
        (SEVERITY_LOW, 'Low'),
    )

    severity = models.CharField(max_length=5, choices=SEVERITIES)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id and not self.created:
            self.created = timezone.now()

        return super(ModerationCategory, self).save(*args, **kwargs)


class ModeratedObject(models.Model):
    description = models.CharField(_('description'), max_length=settings.MODERATED_OBJECT_DESCRIPTION_MAX_LENGTH,
                                   blank=False, null=True)

    approved = models.BooleanField(_('approved'), default=False,
                                   blank=False, null=False)
    verified = models.BooleanField(_('verified'), default=False,
                                   blank=False, null=False)
    submitted = models.BooleanField(_('submitted'), default=False,
                                    blank=False, null=False)

    moderation_object = GenericRelation('openbook_moderation.ModeratedObject', related_query_name='moderated_objects')

    category = models.ForeignKey(ModerationCategory, on_delete=models.CASCADE, related_name='moderated_objects')

    OBJECT_TYPE_POST = 'P'
    OBJECT_TYPE_POST_COMMENT = 'PC'
    OBJECT_TYPE_COMMUNITY = 'C'
    OBJECT_TYPE_USER = 'U'
    OBJECT_TYPE_MODERATED_OBJECT = 'MO'
    OBJECT_TYPES = (
        (OBJECT_TYPE_POST, 'Post'),
        (OBJECT_TYPE_POST_COMMENT, 'Post Comment'),
        (OBJECT_TYPE_COMMUNITY, 'Community'),
        (OBJECT_TYPE_USER, 'User'),
        (OBJECT_TYPE_MODERATED_OBJECT, 'MO'),
    )

    object_type = models.CharField(max_length=5, choices=OBJECT_TYPES)

    # Generic relation types
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        constraints = [
            models.UniqueConstraint(name='reporter_moderated_object_constraint',
                                    fields=['object_type', 'object_id'])
        ]

    @classmethod
    def create_moderated_object(cls, object_type, object_id, category_id):
        return cls.objects.create(object_type=object_type, object_id=object_id, category_id=category_id)

    @classmethod
    def get_or_create_moderated_object(cls, object_type, object_id, category_id):
        try:
            moderated_object = cls.objects.get(object_type=object_type, object_id=object_id)
        except cls.DoesNotExist:
            moderated_object = cls.create_moderated_object(object_type=object_type,
                                                           object_id=object_id, category_id=category_id)

        return moderated_object

    def update_with_actor_with_id(self, actor_id, description, approved, verified, submitted, category_id):
        if description is not None:
            current_description = self.description
            self.description = description
            ModeratedObjectDescriptionChangedLog.create_moderated_object_description_changed_log(
                changed_from=current_description, changed_to=description, moderated_object_id=self.pk,
                actor_id=actor_id)

        if approved is not None:
            current_approved = self.approved
            self.approved = approved
            ModeratedObjectApprovedChangedLog.create_moderated_object_approved_changed_log(
                changed_from=current_approved, changed_to=approved, moderated_object_id=self.pk, actor_id=actor_id)

        if submitted is not None:
            current_submitted = self.submitted
            self.submitted = submitted
            ModeratedObjectSubmittedChangedLog.create_moderated_object_submitted_changed_log(
                changed_from=current_submitted, changed_to=submitted, moderated_object_id=self.pk, actor_id=actor_id)

        if verified is not None:
            current_verified = self.verified
            self.verified = verified
            ModeratedObjectVerifiedChangedLog.create_moderated_object_verified_changed_log(
                changed_from=current_verified, changed_to=verified, moderated_object_id=self.pk, actor_id=actor_id)

        if category_id is not None:
            current_category_id = self.category_id
            self.category_id = category_id
            ModeratedObjectCategoryChangedLog.create_moderated_object_category_changed_log(
                changed_from_id=current_category_id, changed_to_id=category_id, moderated_object_id=self.pk,
                actor_id=actor_id)

        self.save()

    def verify_with_actor_with_id(self, actor_id):
        current_verified = self.verified
        self.verified = True
        ModeratedObjectVerifiedChangedLog.create_moderated_object_verified_changed_log(
            changed_from=current_verified, changed_to=self.verified, moderated_object_id=self.pk, actor_id=actor_id)
        self.save()

    def unverify_with_actor_with_id(self, actor_id):
        current_verified = self.verified
        self.verified = False
        ModeratedObjectVerifiedChangedLog.create_moderated_object_verified_changed_log(
            changed_from=current_verified, changed_to=self.verified, moderated_object_id=self.pk, actor_id=actor_id)
        self.save()

    def submit_with_actor_with_id(self, actor_id):
        current_submitted = self.submitted
        self.submitted = True
        ModeratedObjectSubmittedChangedLog.create_moderated_object_submitted_changed_log(
            changed_from=current_submitted, changed_to=self.submitted, moderated_object_id=self.pk, actor_id=actor_id)
        self.save()

    def unsubmit_with_actor_with_id(self, actor_id):
        current_submitted = self.submitted
        self.submitted = False
        ModeratedObjectSubmittedChangedLog.create_moderated_object_submitted_changed_log(
            changed_from=current_submitted, changed_to=self.submitted, moderated_object_id=self.pk, actor_id=actor_id)
        self.save()


class ModerationReport(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_reports')
    moderated_object = models.ForeignKey(ModeratedObject, on_delete=models.CASCADE, related_name='reports')
    category = models.ForeignKey(ModerationCategory, on_delete=models.CASCADE, related_name='reports')
    description = models.CharField(_('description'), max_length=settings.MODERATION_REPORT_DESCRIPTION_MAX_LENGTH,
                                   blank=False, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(name='reporter_moderated_object_constraint',
                                    fields=['reporter', 'moderated_object'])
        ]

    @classmethod
    def create_post_moderation_report(cls, reporter_id, post_id, category_id, description):
        moderated_object = ModeratedObject.get_or_create_moderated_object(object_type=ModeratedObject.OBJECT_TYPE_POST,
                                                                          object_id=post_id,
                                                                          category_id=category_id
                                                                          )
        post_moderation_report = cls.objects.create(reporter_id=reporter_id, category_id=category_id,
                                                    description=description, moderated_object=moderated_object)
        return post_moderation_report

    @classmethod
    def create_post_comment_moderation_report(cls, reporter_id, post_comment_id, category_id, description):
        moderated_object = ModeratedObject.get_or_create_moderated_object(
            object_type=ModeratedObject.OBJECT_TYPE_POST_COMMENT,
            object_id=post_comment_id,
            category_id=category_id
        )
        post_comment_moderation_report = cls.objects.create(reporter_id=reporter_id,
                                                            category_id=category_id,
                                                            description=description,
                                                            moderated_object=moderated_object)
        return post_comment_moderation_report

    @classmethod
    def create_user_moderation_report(cls, reporter_id, user_id, category_id, description):
        moderated_object = ModeratedObject.get_or_create_moderated_object(object_type=ModeratedObject.OBJECT_TYPE_USER,
                                                                          object_id=user_id,
                                                                          category_id=category_id
                                                                          )
        user_moderation_report = cls.objects.create(reporter_id=reporter_id, category_id=category_id,
                                                    description=description, moderated_object=moderated_object)
        return user_moderation_report

    @classmethod
    def create_community_moderation_report(cls, reporter_id, community_id, category_id, description):
        moderated_object = ModeratedObject.get_or_create_moderated_object(
            object_type=ModeratedObject.OBJECT_TYPE_COMMUNITY,
            object_id=community_id,
            category_id=category_id
        )
        community_moderation_report = cls.objects.create(reporter_id=reporter_id, category_id=category_id,
                                                         description=description, moderated_object=moderated_object)
        return community_moderation_report

    @classmethod
    def create_moderated_object_moderation_report(cls, reporter_id, moderated_object_id, category_id, description):
        moderated_object = ModeratedObject.get_or_create_moderated_object(
            object_type=ModeratedObject.OBJECT_TYPE_MODERATED_OBJECT,
            object_id=moderated_object_id,
            category_id=category_id
        )
        moderated_object_moderation_report = cls.objects.create(reporter_id=reporter_id, category_id=category_id,
                                                                description=description,
                                                                moderated_object=moderated_object)
        return moderated_object_moderation_report


class ModerationPenalty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_penalties')
    duration = models.DateTimeField(editable=False)
    moderated_object = models.ForeignKey(ModeratedObject, on_delete=models.CASCADE, related_name='penalties')

    TYPE_SUSPENSION = 'S'

    TYPES = (
        (TYPE_SUSPENSION, 'Suspension'),
    )


class ModeratedObjectLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', null=True)

    LOG_TYPE_DESCRIPTION_CHANGED = 'DC'
    LOG_TYPE_APPROVED_CHANGED = 'AC'
    LOG_TYPE_TYPE_CHANGED = 'TC'
    LOG_TYPE_SUBMITTED_CHANGED = 'SC'
    LOG_TYPE_VERIFIED_CHANGED = 'VC'
    LOG_TYPE_CATEGORY_CHANGED = 'CC'

    LOG_TYPES = (
        (LOG_TYPE_DESCRIPTION_CHANGED, 'Description Changed'),
        (LOG_TYPE_APPROVED_CHANGED, 'Approved Changed'),
        (LOG_TYPE_TYPE_CHANGED, 'Type Changed'),
        (LOG_TYPE_SUBMITTED_CHANGED, 'Submitted Changed'),
        (LOG_TYPE_VERIFIED_CHANGED, 'Verified Changed'),
        (LOG_TYPE_CATEGORY_CHANGED, 'Category Changed'),
    )

    type = models.CharField(max_length=5, choices=LOG_TYPES)

    # Generic relation types
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    moderated_object = models.ForeignKey(ModeratedObject, on_delete=models.CASCADE, related_name='logs')
    created = models.DateTimeField(editable=False, db_index=True)

    @classmethod
    def create_moderated_object_log(cls, moderated_object_id, type, content_object, actor_id):
        return cls.objects.create(log_type=type, content_object=content_object, moderated_object_id=moderated_object_id,
                                  actor_id=actor_id)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id and not self.created:
            self.created = timezone.now()

        return super(ModeratedObjectLog, self).save(*args, **kwargs)


class ModeratedObjectCategoryChangedLog(models.Model):
    log = GenericRelation(ModeratedObjectLog)
    changed_from = models.ForeignKey(ModerationCategory, on_delete=models.CASCADE, related_name='+')
    changed_to = models.ForeignKey(ModerationCategory, on_delete=models.CASCADE, related_name='+')

    @classmethod
    def create_moderated_object_category_changed_log(cls, moderated_object_id, changed_from_id, changed_to_id,
                                                     actor_id):
        moderated_object_category_changed_log = cls.objects.create(changed_from_id=changed_from_id,
                                                                   changed_to_id=changed_to_id)
        ModeratedObjectLog.create_moderated_object_log(type=ModeratedObjectLog.LOG_TYPE_CATEGORY_CHANGED,
                                                       content_object=moderated_object_category_changed_log,
                                                       moderated_object_id=moderated_object_id, actor_id=actor_id)


class ModeratedObjectDescriptionChangedLog(models.Model):
    log = GenericRelation(ModeratedObjectLog)
    changed_from = models.CharField(_('changed from'), max_length=settings.MODERATION_REPORT_DESCRIPTION_MAX_LENGTH,
                                    blank=False, null=False)
    changed_to = models.CharField(_('changed to'), max_length=settings.MODERATION_REPORT_DESCRIPTION_MAX_LENGTH,
                                  blank=False, null=False)

    @classmethod
    def create_moderated_object_description_changed_log(cls, moderated_object_id, changed_from, changed_to, actor_id):
        moderated_object_description_changed_log = cls.objects.create(changed_from=changed_from,
                                                                      changed_to=changed_to)
        ModeratedObjectLog.create_moderated_object_log(type=ModeratedObjectLog.LOG_TYPE_DESCRIPTION_CHANGED,
                                                       content_object=moderated_object_description_changed_log,
                                                       moderated_object_id=moderated_object_id,
                                                       actor_id=actor_id)


class ModeratedObjectApprovedChangedLog(models.Model):
    log = GenericRelation(ModeratedObjectLog)
    changed_from = models.BooleanField(_('changed from'),
                                       blank=False, null=False)
    changed_to = models.BooleanField(_('changed to'),
                                     blank=False, null=False)

    @classmethod
    def create_moderated_object_approved_changed_log(cls, moderated_object_id, changed_from, changed_to, actor_id):
        moderated_object_description_changed_log = cls.objects.create(changed_from=changed_from,
                                                                      changed_to=changed_to)
        ModeratedObjectLog.create_moderated_object_log(type=ModeratedObjectLog.LOG_TYPE_APPROVED_CHANGED,
                                                       content_object=moderated_object_description_changed_log,
                                                       moderated_object_id=moderated_object_id, actor_id=actor_id)


class ModeratedObjectVerifiedChangedLog(models.Model):
    log = GenericRelation(ModeratedObjectLog)
    changed_from = models.BooleanField(_('changed from'),
                                       blank=False, null=False)
    changed_to = models.BooleanField(_('changed to'),
                                     blank=False, null=False)

    @classmethod
    def create_moderated_object_verified_changed_log(cls, moderated_object_id, changed_from, changed_to, actor_id):
        moderated_object_description_changed_log = cls.objects.create(changed_from=changed_from,
                                                                      changed_to=changed_to)
        ModeratedObjectLog.create_moderated_object_log(type=ModeratedObjectLog.LOG_TYPE_VERIFIED_CHANGED,
                                                       content_object=moderated_object_description_changed_log,
                                                       moderated_object_id=moderated_object_id, actor_id=actor_id)


class ModeratedObjectSubmittedChangedLog(models.Model):
    log = GenericRelation(ModeratedObjectLog)
    changed_from = models.BooleanField(_('changed from'),
                                       blank=False, null=False)
    changed_to = models.BooleanField(_('changed to'),
                                     blank=False, null=False)

    @classmethod
    def create_moderated_object_submitted_changed_log(cls, moderated_object_id, changed_from, changed_to, actor_id):
        moderated_object_description_changed_log = cls.objects.create(changed_from=changed_from,
                                                                      changed_to=changed_to)
        ModeratedObjectLog.create_moderated_object_log(type=ModeratedObjectLog.LOG_TYPE_SUBMITTED_CHANGED,
                                                       content_object=moderated_object_description_changed_log,
                                                       moderated_object_id=moderated_object_id, actor_id=actor_id)
