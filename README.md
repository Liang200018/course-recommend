# Achieve a simple Course Recommendation System
The project used to develop the course recommend web application.  

Code Last updated: April 23, 2022   
Doc Last updated: May 24, 2022
## Thoughts
The system consists of login, course recommendation, course retrieve, admin site for manage the courses.

Recommendation is the core part of the system. The recommendation strategy is always complex to satisfy the needs of users and improve the measure of recommendation system. 

In the system, I adopt some classical algorithms and improvement versions of the algorithms, such as classical item-based collaborative filtering, incremental item-cf and latent factor model.    

The incremental item-cf is nearly real-time, it has a interaction with database during the beginning and ending of session[1].

## Implementation

The development framework of project is Django.

I abstract the PageResource class, PageResourseManagement class, ViewWithPageResource wrapper according to the principle of MVC design patterns.

The HTML template I use is from the blog project[2] because I am not familiar with css, javascript, even Bootstrap and VUE. I have too much time to learn when I were doing the project.  

I deploy it using uWSGI and Nginx at Aliyun server. The database is Mysql.

I learned classical algorithm code from the book written by Xiang Liang[3].

## References
[1] *Incremental Collaborative Filtering for Binary Ratings*, Catarina Miranda and Al´ıpio M. Jorge  
[2] *Django blog development tutorial*, Wu QingFeng, https://www.django.cn/course/course-2.html  
[3] *Recommendation System practice*, Xiang Liang
