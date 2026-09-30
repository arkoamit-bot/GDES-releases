## GDES 7.4.5

A small fix for printing. No database migrations.

### Printing
- **Printing a prescription no longer gives blank pages.** The *Print
  prescription* button on the preview page printed the slip inside the app's own
  page, which came out on real printers as a blank first page with the slip
  pushed onto a later page. The button now opens the slip on its own and prints
  that: one page, as in the saved PDF. Ctrl+P on the preview page does the same.
- *Save as PDF* is unchanged.
