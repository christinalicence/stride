# Testing for Stride

## 1. Testing Objectives Against User Stories

## 2. Manual Testing
### a. Testing Using Code Validators
### b. Accessibility and Performance Testing
### c. Manual Testing of Features
### d. Manual Testing of Responsiveness
### e. User Testing/Feedback

## 3. Automated Testing using Django

## 4. Test Driven Development

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