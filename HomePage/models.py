from django.db import models

class HomePage(models.Model):
    title = models.CharField(max_length=100,default= "আলোকিত জীবনের সন্ধানে রোভারিং")
    description = models.CharField(max_length=200)

    # Hero Section
    hero_image = models.ImageField(upload_to="images/homepage/")
    header_text = models.CharField(max_length=50, default= 'আমাদের সম্পর্কে')


    # About Section
    about_image = models.ImageField(upload_to="images/about/")
    about_title = models.CharField(max_length=150, default='মুন্সীগঞ্জ পলিটেকনিক ইন্সটিটিউট রোভার স্কাউট গ্রুপ')
    about_description_1 = models.TextField()
    about_description_2 = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title