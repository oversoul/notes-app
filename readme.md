# Notes

notes app, obviously for keeping notes. I really struggle to find something lightweight.


## database: sqlite

### tables
- notes
	- id
	- name
	- color
	- content


```sql
CREATE TABLE IF NOT EXISTS notes (id integer PRIMARY KEY AUTOINCREMENT, name varchar(255), color varchar(20), content TEXT);
```

data example:

```sql
INSERT INTO notes(name, color, content) VALUES('Starboard', '#ff0000', "# V Documentation\n## Introduction\n\nV is a statically typed compiled programming language designed for building maintainable software.\n\nIt\'s similar to Go and is also influenced by Oberon, Rust, Swift.\n\nV is a very simple language. Going through this documentation will take you about half an hour,and by the end of it you will learn pretty much the entire language.\n\nDespite being simple, it gives a lot of power to the developer. Anything you can do in other languages,you can do in V.");
```