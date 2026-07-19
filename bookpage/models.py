from django.db import models


class PdfBook(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="gallery/pdfs/")

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title