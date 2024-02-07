"use client";
import ReactConsole from 'react-console-emulator'

import Image from 'next/image';
import Editor from "@monaco-editor/react";
import { useState, useEffect } from 'react';
import TextareaAutosize from "react-textarea-autosize";
import { TbPrompt } from "react-icons/tb";

/* @client-component */
export default function Home() {

  const defaultLibName = 'langchain';
  const defaultLibraryURLs = ['https://langchain-langchain.vercel.app/docs/get_started/'];
  const defaultLibraryRepoURL = "https://github.com/langchain-ai/langchain.git";
  const [text, setText] = useState("");
  const [fileContent, setFileContent] = useState('');
  const [codeerrorMsg, setCoderrorMsg] = useState("");
  const [planContent, setPlanContent] = useState<string>('');
  const [libName, setLibName] = useState(defaultLibName); //useState<string>('');
  const [libraryURLs, setLibraryURLs] = useState(defaultLibraryURLs);//useState<string[]>([]); // list library links
  const [libraryRepoURL, setLibraryRepoURL] = useState(defaultLibraryRepoURL);
  const [textareaContent, setTextareaContent] = useState('');
  const [apiStatus, setApiStatus] = useState<string>("Offline");
  const [generatedCode, setGeneratedCode] = useState<string>('');
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");




  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      const reader = new FileReader();
      reader.onload = function (evt) {
        // evt is of type ProgressEvent<FileReader>
        setFileContent(evt.target?.result as string);
      };
      reader.readAsText(file);
    }
  };

  const handleURLInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const inputUrls = event.target.value.split('\n'); // Splitting by new line for textarea
    setLibraryURLs(inputUrls);
  };

  const checkApiHealth = async () => {
    try {
      const response = await fetch("http://localhost:8000/health");
      if (response.status === 200) {
        setApiStatus("Online");
      } else {
        setApiStatus("Offline");
      }
    } catch (error) {
      setApiStatus("Offline");
    }
  };

  useEffect(() => {
    checkApiHealth();
  }, []);

  const handleGenerateClick = () => {
    setIsLoading(true);
    const ws = new WebSocket('ws://localhost:8000/generate/');
    ws.onopen = () => {
      ws.send(JSON.stringify({
        source_code: fileContent,
        prompt: textareaContent,
        links: libraryURLs,
        libname: libName,
        lib_repo_url: libraryRepoURL
      }));
    };
    ws.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      console.log(data);  // log the data immediately when received
      if (data.plan) {
        setPlanContent(data.plan);
      }
      if (data.code) {
        setGeneratedCode(data.code);
      }
      if (data.error){
        setCoderrorMsg(data.error);
      }
      if (data.is_final) {
        setIsLoading(false);
        ws.close();
      }
    };
    ws.onerror = (error: Event) => {
      console.log(`WebSocket error: ${error}`);
      setIsLoading(false);
    };
    ws.onclose = (event: CloseEvent) => {
      if (!event.wasClean || event.code !== 1000) {
        console.log(`WebSocket connection closed unexpectedly: [${event.code}] ${event.reason}`);
      }
      setIsLoading(false);
    };
  };

  return (
    <div>
      <div className='flex flex-col justify-center items-center mt-24'>
        <Image
          src="/Logo.png"
          alt="Logo"
          width={250}
          height={250}
          className="self-center"
        />
        <p className='font-mono text-zinc-800 text-sm mt-3'>Let CodInit help you to create your ideas with your favorite libaries! 💖</p>
        <div className="mt-4 text-xs text-zinc-900 font-mono flex justify-center">
          <span className="rounded-indicator">v0.1.0</span>
          <span className="rounded-indicator">API: {apiStatus}</span>
        </div>
      </div>

      <div className="flex flex-row justify-center items-center h-auto mt-24">
        <div className="w-1/3 h-96 bg-zinc-100 m-6 rounded shadow-lg p-4 table-container animate-pop-in  border-2 border-dashed border-green-300">

          <div className="flex items-center mb-4">
            <span className="bg-red-500 rounded-full w-2 h-2 mr-1"></span>
            <span className="bg-yellow-500 rounded-full w-2 h-2 mr-1"></span>
            <span className="bg-green-500 rounded-full w-2 h-2 mr-2"></span>
            <span className="font-mono font-bold text-sm text-zinc-800">Code Plan</span>
          </div>
          <Editor
            height="calc(100% - 2rem)"
            defaultLanguage="markdown"
            value={planContent}
            wordWrap="on"  // enables word wrapping in Monaco Editor
          />

        </div>

        <div className=" w-1/4 bg-zinc-100 m-6  p-3 rounded-lg shadow-lg animate-pop-in table-container">
          <div className="flex items-center mb-4">
            <TbPrompt className="mr-2"></TbPrompt>
            <p className="text-sm font-mono font-bold text-zinc-800">Code Prompt</p>
          </div>
          <div className="flex items-center text-zinc-800 font-mono">
            <textarea
              placeholder='What to you want to create?'
              value={textareaContent}
              onChange={(e) => setTextareaContent(e.target.value)}
              className="w-full bg-white text-zinc-800 outline-none font-mono p-3 rounded-lg"
            />
          </div>
          <div className="mt-3">
            <p className="text-xs font-mono text-zinc-800 mb-2 text-center"> Select a library you want to use</p>

            <div className="flex flex-row gap-4"> {/* Flex container with row direction */}

              <div className="flex-1"> {/* First column */}
                <div className="flex items-center text-zinc-800 font-mono">
                  <textarea
                    placeholder='library name'
                    value={libName}
                    onChange={(e) => setLibName(e.target.value)}
                    className="w-full bg-white text-zinc-800 outline-none font-mono p-3 rounded-lg"
                  />
                </div>
              </div>

              <div className="flex-1"> {/* Second column */}
                <div className="flex items-center text-zinc-800 font-mono">
                  <textarea
                    placeholder='documentation URLs'
                    value={libraryURLs.join('\n')}
                    onChange={handleURLInputChange}
                    className="w-full bg-white text-zinc-800 outline-none font-mono p-3 rounded-lg"
                  />
                </div>
              </div>

            </div>

            <div className="flex items-center text-zinc-800 font-mono">
            <textarea
              placeholder='Set Library Repository URL'
              value={libraryRepoURL}
              onChange={(e) => setLibraryRepoURL(e.target.value)}
              className="w-full bg-white text-zinc-800 outline-none font-mono p-3 rounded-lg"
            />
          </div>

          </div>
          <div className="flex justify-center mt-4">
            <button
              className="p-3 my-2 text-sm text-zinc-800 bg-zinc-100 font-mono animate-pop-in-late rounded-lg focus:outline-none shadow-lg hover:bg-green-400 hover:text-white"
              onClick={handleGenerateClick}
              disabled={isLoading}
            >
              {isLoading ? 'Loading...' : '⚙️ Generate'}
            </button>
          </div>
          {errorMsg && <p className="error-message font-mono text-xs text-center">{errorMsg}</p>}
        </div>

        <div className="w-1/3 h-96 bg-zinc-200 m-6 rounded shadow-lg p-4 table-container animate-pop-in  border-2 border-dashed border-blue-300">
          <div className="flex items-center mb-4">
            <span className="bg-red-500 rounded-full w-2 h-2 mr-1"></span>
            <span className="bg-yellow-500 rounded-full w-2 h-2 mr-1"></span>
            <span className="bg-green-500 rounded-full w-2 h-2 mr-2"></span>
            <span className="font-mono font-bold text-sm text-zinc-800">magic_code.py</span>
          </div>
          <Editor
            height="calc(100% - 2rem)"
            defaultLanguage="python"
            value={generatedCode}
          />
        </div>

      </div>
      {/* The error console
      <div
        style={{
          backgroundColor: 'black',
          color: '#00FF00',
          padding: '10px',
          minHeight: '100px',
          whiteSpace: 'pre-wrap', // This allows for multiline error messages
          border: '2px solid red',
          marginTop: '10px',
          fontFamily: 'monospace', // Gives the console-like appearance
          width: '80%', // Adjust the width as per requirement
        }}
        className="mx-auto text-left" // Center the div
      >
        {codeerrorMsg.split('\n').map((line, index) => (
          <p key={index} style={{ paddingLeft: '10px' }}>
            {line}
          </p>
        ))}
      </div>*/}
      <div className="flex justify-center mt-4">
        <div
          className="terminal-style"
          style={{ width: '80%' }}
        >
          <p>You will find the logs here.</p>
          {codeerrorMsg && (
            <div>
              <p>{codeerrorMsg}</p>
            </div>
          )}
        </div>
      </div>

    </div>

  )
}
