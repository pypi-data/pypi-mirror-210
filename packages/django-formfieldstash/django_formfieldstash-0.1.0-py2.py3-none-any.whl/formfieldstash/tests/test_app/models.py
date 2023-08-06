from django.db import models


SELECTION_CHOICES = (
    ('', 'Empty'),
    ('horse', 'Horse'),
    ('bear', 'Bear'),
    ('octopus', 'Octopus'),
)

SET_CHOICES = (
    ('', 'Empty'),
    ('set1', '1'),
    ('set2', '2'),
    ('set3_1', '3'),
)


class TestModelSingle(models.Model):
    selection = models.CharField('Selection', max_length=20, blank=True, choices=SELECTION_CHOICES)
    horse = models.CharField(max_length=20, blank=True, )
    bear = models.DateTimeField(blank=True, null=True, default=None)
    octopus = models.CharField(max_length=20, blank=True, )

    def __str__(self):
        return "Single Stash Test Model: %s" % self.selection


class TestModelSingle2(models.Model):
    selection = models.CharField('Selection', max_length=20, blank=True, choices=SELECTION_CHOICES)
    horse = models.CharField(max_length=20, blank=True, )
    bear = models.CharField(max_length=20, blank=True, )
    octopus = models.CharField(max_length=20, blank=True, )

    def __str__(self):
        return "Single Stash Test Model 2: %s" % self.selection


class TestModelAdvanced(models.Model):
    set = models.CharField('Selection', max_length=20, blank=True, choices=SET_CHOICES)
    set1_1 = models.CharField(max_length=20, blank=True, )
    set2_1 = models.CharField(max_length=20, blank=True, )
    set2_2 = models.CharField(max_length=20, blank=True, )
    set2_3 = models.CharField(max_length=20, blank=True, )
    set3_1 = models.CharField(max_length=20, blank=True, )

    def __str__(self):
        return "Test Advanced Model: %s" % self.set


class TestModelAdvanced2(models.Model):
    set = models.CharField('Selection', max_length=20, blank=True, choices=SET_CHOICES)
    set1_1 = models.CharField(max_length=20, blank=True, )
    set2_1 = models.CharField(max_length=20, blank=True, )
    set2_2 = models.CharField(max_length=20, blank=True, )
    set2_3 = models.CharField(max_length=20, blank=True, )
    set3_1 = models.CharField(max_length=20, blank=True, )

    def __str__(self):
        return "Test Advanced Model 2: %s" % self.set


class TestInlineModel(models.Model):
    parent = models.ForeignKey(TestModelAdvanced, on_delete=models.CASCADE)
    parent2 = models.ForeignKey(TestModelAdvanced2, on_delete=models.CASCADE, default=None, null=True)
    title = models.CharField(max_length=20, blank=True, )

    def __str__(self):
        return "A Simple Inline Model: %s" % self.title


class TestModelInInlineModel(models.Model):
    title = models.CharField(max_length=20, blank=True, )

    def __str__(self):
        return "Has Stash In Inline Model: %s" % self.title


class TestInlineModelSingle(models.Model):
    parent = models.ForeignKey(TestModelInInlineModel, on_delete=models.CASCADE)
    selection = models.CharField('Selection', max_length=20, blank=True, choices=SELECTION_CHOICES)
    horse = models.CharField(max_length=20, blank=True, )
    bear = models.CharField(max_length=20, blank=True, )
    octopus = models.CharField(max_length=20, blank=True, )

    def __str__(self):
        return "Inline Stash Model: %s" % self.selection
