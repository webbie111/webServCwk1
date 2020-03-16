from django.db import models

class Module(models.Model):
    module_code = models.CharField(max_length = 4, unique = True)
    module_name = models.CharField(max_length = 50, unique = True)

    def __str__(self):
        return u'%s %s' % (self.module_code, self.module_name)

class Professor(models.Model):
    prof_code = models.CharField(max_length = 4, unique = True)
    prof_name = models.CharField(max_length = 30)

    def __str__(self):
        return u'%s %s' % (self.prof_code, self.prof_name)

class ModuleInstance(models.Model):
    module_id = models.ForeignKey(Module, on_delete = models.CASCADE)
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField()
    taught_by = models.ManyToManyField(Professor)

    def __str__(self):
        return u'%s %d %d ' % (self.module_id.module_code, self.year, self.semester)+', '.join([str(professor) for professor in self.taught_by.all()])

class Rating(models.Model):
    rating = models.PositiveSmallIntegerField()
    professor = models.ForeignKey(Professor, on_delete = models.CASCADE)
    module_instance = models.ForeignKey(ModuleInstance, on_delete = models.CASCADE)

    def __str__(self):
        return u'%d %s %s %d %d' % (self.rating, self.professor.prof_name, self.module_instance.module_id.module_code, self.module_instance.year, self.module_instance.semester)
