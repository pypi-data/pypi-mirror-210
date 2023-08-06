# TIME PRINT README FILE
This is a python package to use write effect and more in your texts !

## TP(seconds,"text")
You want to write "your_text" in 5 seconds? just use;
TP(5,"your_text") !
formats: seconds: int,"text":str
## P("text")
You don't want to wait until it writes bla bla seconds ?
it just goes write effect and its fast (very fast)

format: "text":str
## timetag(format:str)
Its not very cool thing but i added
don't have to talk just look ex.
format usages;
"%H:%M" Returns --> 12:56 = (Hours:Minutes)
"%H:%M:%S" Returns --> 12:56:24 = (Hours:Minutes:Seconds)
"%d.%m.%y" Returns --> 10.02.2023 = (Day.Month.Year)

It uses strftime package.
## info()
just info about package.