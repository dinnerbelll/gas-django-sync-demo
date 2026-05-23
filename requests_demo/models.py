from django.db import models


class DemoRequest(models.Model):
    student_name = models.CharField(max_length=255)
    problem_text = models.TextField()
    submitted_at = models.DateTimeField()
    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at", "-created_at"]

    def __str__(self):
        return f"{self.student_name} - {self.submitted_at.isoformat()}"
