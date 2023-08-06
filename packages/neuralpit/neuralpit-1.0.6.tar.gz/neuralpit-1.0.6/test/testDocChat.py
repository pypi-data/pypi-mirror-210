from neuralpit.tools.chat import ChatWithDocument
import os

def main():
   chat = ChatWithDocument()
   fileName = 'manual.pdf'
   with open(fileName, mode='rb') as file: # b is important -> binary
      file_content = file.read()
      chat.addFile(file_content)
      question ='How to change battery'
      ans = chat.response(question)
      print(ans)

if __name__ == "__main__":
    main()
