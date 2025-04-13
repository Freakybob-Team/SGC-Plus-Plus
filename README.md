# SGC++

A remake of SigmaGreg.

## To-Do List:

- [x] Variables
- [x] Functions **(new, expect bugs)**
- [x] If statements
- [x] Typing for variables **(new, expect bugs)**
- [x] While loops **(new, needs to be fixed)**
- [x] For loops   **(new, needs to be fixed)**
- [x] Input
- [x] Output **(ass)**
- [x] Comments
- [x] Error handling
- [ ] Move to-do items to individual GitHub issues <!-- grrr -->
- [x] Python modules
- [ ] Every freaking thing


## Better Syntax
**Just look at this!!!**

```
import requests
import sgcm
import webbrowser

var url = "https://dog.ceo/api/breeds/image/random"
var request = requests.get(url)

if (request.status_code == 200):
    var json = request.json()
    var pretty = sgcm.prettyPrint(json)
    gPrintln(pretty)
    if ("message" in json):
        var w = gReadln("do you want to open image in browser? \p1y or n\p2: ")
        if (w.lower() == "y"):
            var image = json["message"]
            webbrowser.open(image)
        elif (w.lower() == "n"):
            gPrintln("ok...")
        else:
            gPrintln("what")
else:
    gPrintln("error")
```

**WAY better than SigmaGreg's syntax..**

```
credit_number:
ssn:
credit_num_back:

gregPr "I need your credit card number to make sure you not hacked\n"
gregIn credit_number
gregPr "Thank you, now I need your social security to make sure to identity fraud\n"
gregIn ssn
gregPr "thank you, now I need 3 number on back to make sure your bank account safe\n"
gregIn credit_num_back

gregPr f"Ok so I have {credit_number}, {ssn}, and {credit_num_back}\n"
gregPr "ghahahaha you have been hacked hahgahgahah" 
```

---


# Why is this better?

  **First of all:**

  - SigmaGreg had bad syntax, you could barely do anything and there were so many things that was bad about it. SGC++ will fix all of that.
  - Nicer looking keywords (eg: ```gPrintln()```) unlike the original SigmaGreg Code (eg: ```gregPr```)
  - Not as buggy!!!

---

# What does the new Syntax keywords mean???

### gPrintln()
  > gPrintln() is how you would print, just like `gregPr`.
### gReadln()
  > gReadln() is how you take input. It's the exact same as `gregIn`

---

<p align="center">
  2024-2025 Freakybob-Team. Everything is licensed under MIT.
</p>
<p align="center">
<img src="src/assets/logo.ico" width="40" height="40" alt="Sg_logo.png"/>

</p>


<p align=center>
    <small>THIS IS VERY NEW. EXPECT BUGS.</small>
</p>
