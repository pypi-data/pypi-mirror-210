# What is it?

**html_msg** is a Python package that provides functionality to build up HTML messages via simple methods, without the need to write HTML code manually.

# Main Features

Here are a few of the things that **html_msg** does well:

* Easy adding of plain text into message
* Creation of tables and adding them into message
* Easy formating of text and tables via CSS properties
* Rendering and displaying of HTML message in IPython notebook

# Where to get it

```
# PyPI
pip install html-msg
```

# Documentation

## Getting started


Import main classes from the package. 

```
from html_msg import HTMLMessage, HTMLTable
```

## Message creation

Now let's create a message and add there some text.

```
# Create an instance of HTMLMessage
message = HTMLMessage()

# add line of text into message
message.insert_text('Hello, Dears!')

# add another line of text, but on new line this time
message.insert_text('Here are the latest news...', new_line=True)

# in order to add an empty line, pass an empty string to the method 'insert_text'
message.insert_text('', new_line=True)

# and let's add another line of text, but this time it should be bold
bold_text_style = {'font-weight':'bold'}
message.insert_text('Must be this line of text is important!', 
                    new_line=True, 
                    style_dict=bold_text_style)
```

In order to see, what we created, use the method 'display'. 
Please note, that this method uses IPython functionality. 

```
message.display()
```

The result should look like this:
  
Hello, Dears!  
Here are the latest news...  
  
**Must be this line of text is important!**

## Table creation

Let's create a table and fill it with some data

```
# create list that contains table headers
table_headers = ['Item', 'Price', 'quantity']

# rows are represented as list of lists. Every list is a row. 
initial_rows = [ 
    ['Apple', 10, 245], 
    ['Orange', 25, 199] 
]

# create an instance of HTMLTable, pass arguments that were defined above
table = HTMLTable(rows=initial_rows, headers=table_headers)
```

We can add rows whenever we want to:

```
# in order to add a row to the table, use method 'add_row'
table.add_row(['Pear', 19, 387])
```

Or change headers, if necessary:

```
table.set_headers(['Goods', 'Net price', 'Amount'])
```

There are several design presets that you can apply to the table, in order to see them, use method 'show_table_design_presets'

```
table.show_table_design_presets()
```

By default, preset 'Basic' is used, but you can apply any design you like better via the method 'apply_design_preset'

```
table.apply_design_preset('Grey')
```

In order to insert the table into the message, you first need to transform the table into HTML code  
and then insert this HTML into the message body.

```
# transforming table into html code, which is contained in string format
table_html = table.to_string()

# inserting table into message body
message.insert_html(table_html)
```

## Transformation to HTML code

Now, we can transform this message to HTML code in order to send it.  
Please note that this library does not provide functionality to send messages.  
One should use other libraries for that. 

```
# the method 'to_string' returns HTML code in string formart. 
# One can pass it to abstract email sender, which will send it to the recepient.
html_code = message.to_string()
```
