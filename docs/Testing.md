# Testing for Stride

## 1. Testing Objectives Against User Stories
### b. User Stories

## 2. Manual Testing
### a. Testing Using Code Validators
### b. Accessibility and Performance Testing
### c. Manual Testing of Features
### d. Manual Testing of Responsiveness
### e. User Testing/Feedback

## 3. Automated Testing using Django

## 4. Test Driven Development

## 1. Testing Objectives Against User Stories

## 1. User Experience
### a. Purpose of the Website

This is a web application designed to help people formulate ongoing exercise plans with the help of AI taking in to account any injuries or limitations, such as a long term knee injury. The application also strives to create a community where you can follow people and comment on their profiles and traning plans. The idea is that the site will be a positivie place that helps people stay fit, healthy, happy and connected, even if they have injures and/or long term limitations in their exercise. The site is designed to one day make it compatible with smart watches (eg Garmin or Apple) to be able to upload your exercise plan on to your watch to follow.

### b. User Stories

#### First Story

User A has a long term knee injury that means they avoid jumpling and high impact exercises. Every exercise plan they find online seems to suggest this as part of their routines and they are looking for a plan that will adapt to their speicific needs.

 - They needs to be able to tell the AI that generates the plan about their specific exercise needs for a plan. 
 - It is useful for them if the site can remember their injury and build long term progression goals/plans.

#### Second Story

User B enjoys personally adapted plans but also wants to reach out to other people, connect and talk about the challenges they face exercising.

- They need to be able to hold back to back conversations with people on comments

#### Third Story

User C is part of a friendship group that enjoy exercise. They want to be able to see and discuss their friends' plans.

- They need to be able to find the profiles they follow easily and comment on profiles.

#### Fourth Story

User D is an influencer with a community of followers. They want to be able to show their followers the plans they are following.

- They need to be able to exapnd on their profile to communicate to their followers.
- They also need to be able to comment on their own profiles as well as other peoples to help engagement.



## 2. Manual Testing
### a. Testing Using Code Validators

#### HTML validator

All the HTML pages were passed the [W3C HTML Validation Tester](https://validator.w3.org/)




#### CSS Validator

The site passed the [W3C CSS Validation Test](https://jigsaw.w3.org/css-validator/) without errors

![Error free CSS test](docs/docs-images/css-test.png)

#### Python Standards

### b. Accessibility and Performance Testing

The pages were tested using Google Lighthouse for performance, accessibility and Best Practice.

Here is the report for the home page
![Google Lighthouse Report](docs/docs-images/lighthouse-home.png)


Lighthouse did uncover an issue on my traning plans where ther buttons colours used didn't have sufficient contrast.

![buttons in old colour](docs/docs-images/button-contrast.png)

As accessibility is a core part of the ethos of this site I changed the buttons to a darker colour.

![buttons in new colour](docs/docs-images/button-contrast-new.png)

It also picked up on Cloudinary leaving 3rd party cookies as part of it's best practice report on profile pages where an image was being stored.

![78% Best Practice Score on Lighthouse](docs/docs-images/cloudinary-error1.png)

It also showed that it was leaving a marker for the cookies on the issues panel

![Issues warning showing on Lighthouse](docs/docs-images/cloudinary-error2.png)

As I feel that Cloudinary is a useful part of this site I hae decided not to change it, despite these warnings.

These were the only issues across the site found by Lighthouse.


### c. Manual Testing of Features
### d. Manual Testing of Responsiveness
### e. User Testing/Feedback

## 3. Automated Testing using Django

There are lots of tests written and contained in the files test_forms.py, test_tasks.py and test_views.py. They have been designed to ensure that the site works against user stories, but also to make sure that the site is robust and can function when unexpected things happen.

## 4. Test Driven Development

I adopted test driven development part way through this project and started to understand the real benefits of this approach. It has made my code more robust and less prone to errors. It also makes me think about exactly what function I want it to perform before writing it.


### e. User Testing/Feedback

I recieved quite a lot of user feedback when it was tested about 60% through development.

- The profile/edit/profile and generate plan process was too complex. I needed to simplify it in order to make it more user friendly and be able to find the key fields more easily, especially long term injuries/limitations. 

- Also the views of the profiles needed to be different, more detail was needed when you follow someone.

- Input fields, ie weight and target date need to be managed more clearly in the forms. There needs to be a clear error message if any of the inputs are not accepted.

- Several bugs were also uncovered:
    - You can generate training plans on anyone's profile.
    - You can follow yourself.
    - Changes weren't being saved after editing your profile.

I did another bit of user testing when I around 95% through development.

- 


## 3. Automated Testing.

I have set up automated tests in django for all views and forms to ensure as comprehensively as possible that these work.

## 4. Test Driven Development

I picked up the principle of test driven development part way through the project. For the 2nd half of the project all tests were adapted or new tests were written when there was any changes in the views or forms.