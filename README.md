LMTAS
===================

### (Let Me Take A Selfie)

#### What?
Managing fares, splitting bills, keeping track of who owes whom how much has always been a problem, especially in the post-demonetization age (or even before, if you ever stayed in college! :P). Multiple apps like Walnut and Splitwise have come up to try to solve the problem, to different degrees of success.

With LMTAS (Let me take a selfie!), we try to make this problem a thing of the past, by bringing together Face recognition, Push messaging and third party AI/ML tools to make bill management as simple as open up your phone, fire up the app, take a selfie, and ... That's it! Yup, no more browsing through contacts to find people to add to bills, no more messing around with names and groups. It's that simple!

Want to exclude someone? No problem! Want to split by percentages? No problems either! LMTAS brings together multiple APIs ranging from Facial recognition APIs, Push Notification APIs, ML/AI APIs, Social APIs (like Facebook, depending on time constraints), and internal Android APIs to ensure that your parties never have to end again with "Bhai, yeh bill Splitwise pe add kar dena!"

----------


#### Why?

Because we can... Well, also because this was a hack created as part of [Go Hack 2017](https://go-hack.hackerearth.com/sprints/go-hack-1/), held at the Go-Jek campus in Bangalore

----------

#### How?
The original plan was to set up [OpenFace](https://cmusatyalab.github.io/openface/) and train it on a set of photos. However, the short format of the hackathon meant there were compromises to be made.
In the end, the hack makes use of the [Microsoft Cognitive Services APIs](https://www.microsoft.com/cognitive-services/en-us/apis)  and [Kairos](https://www.kairos.com/) for the actual face recognition task. We use [Firebase](firebase.google.com) for Push Notifications/Cloud Messaging and the simple but beautiful [Flask](flask.pocoo.org/) microframework to bring the backend together. Of course, there's a lot of plumbing using [MySQL](dev.mysql.com/downloads/), [Requests](docs.python-requests.org/), [Bootstrap](getbootstrap.com/), and [JQuery](https://jquery.com/) among other frameworks.

----------


#### The Other How?
1. `git clone https://github.com/navinpai/LMTAS.git`
2. Create a DB named gohack
3. `cd LMTAS`
4. `mysql -u root -p gohack < gohack.sql`
5. `cd server`
6. `pip install -r requirements.txt` (You may prefer to virtualenv first)
7. Copy `constants_dummy.py` into `constants.py` and fill in all API keys
8. `python app.py`
9. Backend/Webapp is now up!
10. `cd ../android`
11. Create google-services.json for Firebase.
12. Rename URL in Activitites with your server base URL
13. Build APK and install

----------

#### License Kya Hai?
It's all under [MIT](https://opensource.org/licenses/MIT) baby!
