# ReaderBook
#### By Daniel Reader
#### A simple python web application to allow users to create their own online library.
#### Video Demo:  <https://youtu.be/qU_g4JiyunM>
## Technologies Used
- Python3
- HTML
- CSS
- Django
- Flask
## Description
This is a web application created using Python3, Django and flask that allows users to create their own online libraries. This allows the user to create an account individual to themselves. In the account they are able to add books to the "My Books" section which keeps track of all the books they currently own. They are also able to keep track of the books they wish to own in future in the "My Wishlist" section.
### Books.db
This file holds the backend database that includes information on the user once the user has registered but also includes the information for any owned book and any book added to a user’s Wishlist. The tables include the following:

- ```users``` - This table holds the information on the user once tehy have registered including a hash of the password.
- ```ownedbooks``` - This table holds the book ID and client ID once a user has chosen to add the book to their own library.
- ```wishlist``` - This holds the book ID and client ID for any book that a user has chosen to put on their Wish List
### App.py
This includes the majority of the backend functions to help create the web application, produce information on the books for the user and to refer to the database where needed.
- ```Apology``` - This function redirects the user to an Error page where it will explain to the user the reason for the error. For example "Username already in use".
- ```Login_required``` - This function checks if a session has already been created. If there is not a session in place it redirects the user to the login page to login to their account. If a user has a session already it will continue to move through the web application as requested.
- ```get_isbn``` - Once the user uses the search input on search.html this function utilises the Open Library Search API to retrieve the specific ISBN number (individual book id) that meet the search parameters and returns these as a list called "isbn".
- ```get_book``` - This takes the input as ISBN numbers as a list and retrieves the specific information from the Open Library Book API for these specific book ID's. This then stores the data and returns this to utilise on the pages index.html, results.html and mywishlist.html.
- ```register``` - The user initially will need to register themselves for an account using certain information. This function confirms the information that is input is correct and if so stores the data in books.db to retrieve at a later date. If any information is missing or input incorrectly this will also produce and Error using the ```apology``` function explaining the reason.
- ```login``` - A user will need to login to access their account. This function will validate the details and if correct it will create a session for the user.
- ```logout``` - This function clears the current user session and redirects them to the login page.
- ```index``` - Once a user has logged in they will see the page index.html. This function retrieves the necessary information from books.db for the specific user and uses that information as an input to the ```get_book``` function. This retrieves the information needed to display the currently owned books on the web page.
- ```search``` - This function gets the value from the input on the search.html page and passes this information to the ```get_isbn``` function to get the specific results. Then passes the result of this to ```get_book``` function to retrieve the necessary information for those specific books to show on the results.html page.
- ```addbooks``` - This takes the information from the users input of the book they want to add to the current owned books and saves this information in books.db. If this is a duplicate it will return an error using the ```apology``` function stating the book is already in the owned books list. In addition this also checks the wishlist database and if the user has previously added to their wish list, this removes the specific input from the wish list.
- ```removecurrent``` This deletes a specific record from books.db at the users request, removing it from the currently owned books.
- ```addwishlist``` Similar to the ```addbooks``` function this take the users input and saves the information in books.db, adding the specific book to their wish list. Again this checks to ensure the book is not in the users owned books or the my wish list and returns the approriate error using the ```apology``` function
- ```mywishlist``` This function retrieves the information from books.db and passes the specific values through the ```get_book``` function to retrieve the necessary information and return these values to produce in the Wish List.
- ```removewishlist``` Similar to the ```removecurrent``` function, this removes the specific book ID from the books.db database and therefore removing from the users Wish List.
## Setup/Installation Requirements
- Clone this repository to your desktop.
- Navigate to the top level of the directory.
- Open static/index.html in your browser.
## Known Bugs
- Not all book images load correctly from Open Library Book API.
## Finally
A big thank you to all the people involved with creating __CS50's Introduction to Computer Science__.

Copyright (c) 2022 Daniel Reader.
