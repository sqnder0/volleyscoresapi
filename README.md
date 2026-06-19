# Volleyscoresapi 🏐

> Developer-friendly access to Belgian volleyball data.

A modern REST API that pulls Belgian volleyball data for you.

![API in action](https://s13.gifyu.com/images/bdLuX.gif)<br>
*Example call with curl.*

## 📚 The docs

The docs are available through a [Swagger](https://volleyapi.sqnder.dev/docs) interface (my favorite) or in [ReDoc](https://volleyapi.sqnder.dev/redoc) format.

You can easily run queries through the Swagger interface. I recommend first searching for a club or team and then fetching that club or team by its label and club/team ID.

Some clubs you can look up:

* "Maaseik"
* "Knack"
* "Volley Haasrode Leuven"
* "Lindemans Aalst"

## ✨ Features

At the moment, the API provides:

* Search for clubs
* Search for teams
* Parse clubs by ID
* Parse teams by ID

If you check the [Swagger](https://volleyapi.sqnder.dev/docs) UI, it should speak for itself.

## 🤔 Why?

[volleyscores.be](https://volleyscores.be) is the official source for Belgian volleyball data, but it doesn't provide a public API.

This project exposes that data through a modern REST API so developers can easily integrate it into their own applications without having to reverse engineer the website themselves.

## ⚙️ How it works

The website I'm fetching this data from, [volleyscores.be](https://volleyscores.be), is the official website of the Belgian volleyball organization in Flanders.

It doesn't offer a public API and is pretty outdated. It serves a single `index.php` page that's difficult to navigate due to its heavy reliance on JavaScript.

I fixed this by decoding the network requests that the website makes behind the scenes and parsing them into a developer-friendly format. These aren't API endpoints, but they contain all the data needed to build one.

### API implementation

For the API part, I use [FastAPI](https://fastapi.tiangolo.com/), which I had never used before. I mainly picked it as an opportunity to learn something new. Previously, I always used Flask or Django.

It was surprisingly easy to learn because it feels very similar to Flask while providing a lot of functionality out of the box.

### Scraping and parsing

For scraping and parsing, I use [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/en/latest/).

Initially, I used Playwright, but that didn't work out for me because navigating the site for every request was simply too slow. Luckily, I managed to discover the network requests the site makes, which allowed me to bypass that overhead entirely and made the API a million times faster.

---

Made with ❤️ by [Sqnder](https://github.com/sqnder0/)
