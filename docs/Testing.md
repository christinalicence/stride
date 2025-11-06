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



## 2. Manual Testing
### a. Testing Using Code Validators
### b. Accessibility and Performance Testing
### c. Manual Testing of Features
### d. Manual Testing of Responsiveness
### e. User Testing/Feedback

## 3. Automated Testing using Django

There are lots of tests written and contained in the files test_forms.py, test_tasks.py and test_views.py. They have been designed to ensure that the site works against user stories, but also to make sure that the site is robust and can function when unexpected things happen.

## 4. Test Driven Development

I adopted test driven development part way through this project and started to understand the real benefits of this approach. It has made my code more robust and less prone to errors. It also makes me think about exactly what function I want it to perform before writing it.

## 2. Manual Testing

### e. User Testing/Feedback

I recieved quite a lot of user feedback when it was tested about 60% through development.

- The profile/edit/profile and generate plan process was too complex. I needed to simplify it in order to make it more user friendly and be able to find the key fields more easily, especially long term injuries/limitations. 

- Also the views of the profiles needed to be different, more detail was needed when you follow someone.

- Input fields, ie weight and target date need to be managed more clearly in the forms. There needs to be a clear error message if any of the inputs are not accepted.

- Several bugs were also uncovered:
    - You can generate training plans on anyone's profile.
    - You can follow yourself.
    - Changes weren't being saved after editing your profile.


## 3. Automated Testing.

I have set up automated tests in django for all views and forms to ensure as comprehensively as possible that these work.

## 4. Test Driven Development

I picked up the principle of test driven development part way through the project. For the 2nd half of the project all tests were adapted or new tests were written when there was any changes in the views or forms.