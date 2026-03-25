# Capstone Mini-Challenge — Music Catalog

You have a music catalog database with four tables:

  artists  — id, name, country
  genres   — id, name
  albums   — id, title, artist_id, year_released, genre_id
  tracks   — id, title, album_id, track_number, duration_sec

Use  .tables  and  .schema <table>  to explore the data before you start.

---

## Questions

Answer each question with a single SQL query.
Write your final queries to  capstone_answers.sql  in this folder.

1. List every artist name and the country they are from, sorted alphabetically
   by name.

2. How many albums are in the catalog?

3. Which genre has the most albums?  Show the genre name and the count.

4. List all album titles released before 1970, along with the artist name.
   (Hint: you will need a JOIN.)

5. Find the longest track in the catalog.  Show its title, the album title,
   and its duration in minutes and seconds formatted as  MM:SS.
   (Hint: duration_sec / 60 gives minutes; duration_sec % 60 gives seconds.)

6. How many tracks does each album have?  Show album title and track count,
   sorted by track count descending.

7. List all artists who have released more than one album.

8. Find all tracks longer than 5 minutes (300 seconds).  Show track title,
   album title, and artist name.

9. What is the average track duration (in seconds) across all albums, grouped
   by genre?  Show genre name and average duration rounded to 1 decimal place.

10. Which artist has the most total tracks across all their albums?
    Show the artist name and total track count.

---

## Bonus Challenge

Write a single query that returns for each album:
  - album title
  - artist name
  - genre name
  - number of tracks
  - total duration in minutes (rounded to 1 decimal)

Order by total duration descending.
