# About

`pyqt5span` is a library extending the PyQt5 framework to provide a way of spanning the
horizontal and vertical headers of a `QTableView`. Below is a demonstration of this library
with the script `example.py` in the `samples` directory:

![Example][example-gif]

The source code was adapted from [eyllanesc's solution][eyllanesc-ghrepo] for [this StackOverflow question][so-question-46469720],
which originally supports the spanning of a header by turning it into a grid. Since that
solution is meant for a complex use case, it results in an overcomplicated API for simpler
cases where the user only wants to span rows or columns of standard headers (that is, when
the user doesn't want a grid header). Hence this small library.

  [example-gif]: <samples/example.gif>
  [eyllanesc-ghrepo]: <https://github.com/eyllanesc/stackoverflow/tree/master/questions/46469720>
  [so-question-46469720]: <https://stackoverflow.com/questions/46469720/how-to-make-a-qheaderview-multilevel>