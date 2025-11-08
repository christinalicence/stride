# stride

## Table of Contents

### 1. User Experience
#### a. Purpose of the Website
#### b. User Stories
#### c. Wireframes
#### d. Accessibility
#### e. Colour Palette
#### f. Fonts
#### g. Features
#### h. User Interface Design Decisions

### 2. Database Desgin
#### a. ERD Diagrams
#### b. Schemas

### 3. Technologies Used
#### a. Software Used
#### b. APIs Used
#### c. Other Code Credits

### 4. Deployment Information
#### a. Version Control
#### b. Deployment to Heroku
#### c. Clone the Code Locally

### 5. Testing (See seperate Testing.md file)

### 6. Improvements for Future Releases

### 7. Credits

## 1. User Experience
### a. Purpose of the Website

This is a web application designed to help people formulate ongoing exercise plans with the help of AI taking in to account any injuries or limitations, such as a long term knee injury. The application also strives to create a community where you can follow people and comment on their profiles and traning plans. The idea is that the site will be a positivie place that helps people stay fit, healthy, happy and connected, even if they have injures and/or long term limitations in their exercise.

### b. User Stories

#### First Story

User A has a long term knee injury that means they avoid jumpling and impact. Every exercise plan they find online seems to suggest this as part of their routines and they are looking for a plan that will adapt to their speicific needs.

 - They needs to be able to tell the AI that generates the plan about their specific exercise needs for a plan.

#### Second Story

User B enjoys personally adapted plans but also wants to reach out to other people, connect and talk about the challenges they face exercising.

- They need to be able to hold back to back conversations with people on comments

#### Third Story

User C is part of a friendship group that enjoy exercise. They want to be able to see and discuss their friends plans.

- They need to be able to find the profiles they follow easily and comment on plans.

#### Fourth Story

User D is an influencer with a community of followers. They want to be able to show their followers the plans they are following.

- They need to be able to exapnd on their profile to communicate to their followers.
- They also need to be able to comment on their own plans as well as other peoples to help engagement.


### c. Wireframes

I tried to keep the design of the site fairly simple and this is reflected in the wireframes. The wireframe for the homepage is 

[text](docs-images/home-page.bmpr)

### d. Accessibility
### e. Colour Palette
### f. Fonts

For this project I used Google Fonts Jost, designed to be clear and readable.

### g. Features

The site has several features.

The primary feature is the ability to create bespoke training plans that take injuries or limitations in to account. The plans are created by AI powered by Anthropic. The information is gathered on people's profiles and used by the AI when designing plans.

It also allows users to follow other people and be followed by other people. This is useful if you want to see other traning plans or get an understanding of other people's exercise routines. 

You can comment on plans or profiles to communicate with each other, and the comments have full CRUD functionality.

### h. User Interface Design Decisions

## 2. Database Desgin

### a. ERD Diagrams

### b. Schemas

## 3. Technologies Used

I have used Celery to handle the async tasks while making the API calls. I have used Redis to act as a messenger with Celery

### a. Software Used

The site is built using Python, HTML and CSS on Django 5.2.7. There is a full list of sofware dependencies in the requirements.txt file.

### b. APIs Used

The site uses Anthropic AI API, model claude-haiku-4-5-20251001. The software associated with it sometimes needs updating.

### c. Other Code Credits

## 4. Deployment Information
### a. Version Control
### b. Deployment to Heroku
### c. Clone the Code Locally

## 5. Testing (See seperate Testing.md file)

See Testing.md file for an expalanation of how the site has worked against the user stories, the automated testing strategy and manual testing that has been carried out.

## 6. Security Concerns.

The API key for Anthropic, databse url, Django secret key and Redis key are all stored in .env and have been included in my gitignore, so not uploaded to github.

A security concern tht is ongoing is not having email verification (so people could make multiple accounts and overuse the API leading to high costs). This is something I would look to add in the future.



7. ## Improvements for Future Releases

The biggest plan for the future of this site is to make it compatable with smart watches so that you can save your workouts to the watches and the watches can evaluate your performance during the workouts. This is why the plans are returned in a json format from the AI, to allow them to be uploaded to a watch or other tracker. You could also do a lighter version by allowing syncing with a phone app.

I'd like to put seperate usernames and display names.

I'd like to set up a private messaging system between users.

I'd like to allow comments to contain photos and for all photos associated with someone's profile to be saved in an area that is easy to access.

I'd like to make pages where you can see a list of everyone you are following and a list of all your followers

I'd like to generate some example plans for the homepage to give the user an idea of how they work.

I'd like to change the meta tag refresh on the plan detail.html page to a javascript function to create a more seamless user experience. This would also involve a timer wheel to show that things are happening behind the scenes.

I'd like to put proper email verification on to the program to improve security.

8. ## Things I have learnt 


9. ## Concerns for the future/if I was to put this project live

The thing that would worry me most about putting this project live is the potential for people to make lots of plans and build up the costs for using the AI API.