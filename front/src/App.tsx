
import React, {  useEffect, useRef, useState }from 'react';
import './App.css';
import { transformText } from './utils';
import { fetchGame, fetchGuess } from './api';


type NoWhitespace = "";
type Whitespace = '\u00A0';
type LineReturn = "\u000A";
type UnknownWhitespace = "🫥";

export const whitespaceMap = (whitespace: string): Whitespace | NoWhitespace | LineReturn | UnknownWhitespace => {
  if (whitespace === ' ') 
    return '\u00A0'
  if (whitespace === '\n')
    return '\u000A'
  if (whitespace === '')
    return ''
  else return "🫥"
}

type TokenId = string;

export type Token = {
  id: TokenId
  length: number,
  display?: string
  whitespace: string
  found?: boolean
}

export type Document = {
  title: Token[],
  content: Token[]
}

export type Guess = {
  word: string,
  matches: Record<TokenId, number | string>
}

// const title = transformText("Chateau fort")
// const content = transformText("Le chateau fort est un batiment fortifié", title.length)


const gameId = "2";

function App() {

  const [document, setDocument] = useState<Document|null>(null)
  const [guesses, setGuesses] = useState<Guess[]>([])
  const [word, setWord] = useState('');

  useEffect(() => {
    (async function startFetching() {
      setDocument(null);
      const result = await fetchGame(gameId);
        setDocument(result);
    })()
  }, [])

  const buttonRef = useRef<HTMLButtonElement>(null); // Step 1: Create a reference to the button

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      buttonRef.current?.click(); 
    }
  };
  
  const handleSubmitGuess = async () => {
    const guessResponse  = await fetchGuess(gameId, word)
    setGuesses([...guesses, guessResponse])
    setWord('')
  };

  const formatSimilarWord = (token: Token, word: string) => {
    if (word.length >= token.length) 
      return word
    return word + Array(token.length - word.length).fill('\u00A0').join('')
  }

  const formatToken = (token: Token)  => {
    let freshlyFound = ""
    let colorStyle = ""
    // exact word found
    const foundIndex = guesses.findIndex((guess) => typeof guess.matches[token.id] === "string")
    const foundText  = guesses[foundIndex]?.matches[token.id] as string | undefined
    if (foundText) {
     token.display = foundText
     token.found = true
     freshlyFound = foundIndex === guesses.length - 1 ? "fresh" : ""
    } else {
      // Similar word found
      const similarIndex = guesses.findIndex((guess) => typeof guess.matches[token.id] === "number")
      const similarityScore = guesses[similarIndex]?.matches[token.id] as number | undefined
      
      if(similarityScore) {
        const greyLevel =  Math.floor(255 * (1 - similarityScore));
        colorStyle = `rgb(${greyLevel}, ${greyLevel}, ${greyLevel})`;
        token.display = formatSimilarWord(token, guesses[similarIndex].word)
      } 
    }
    const className = token.found ? "show": "secret"
    const text = token.display ?? Array(token.length).fill('\u00A0').join('')
    return (<>
      <span key={token.id} id={token.id} className={["w", className, freshlyFound].join(" ")}  style={{ color: colorStyle }}>{text}</span>
      <span className="w">{whitespaceMap(token.whitespace)}</span>
      </>
    )
  }

  return (
    <div className="App">
      {document ? (
      <>
        <header className="doc-title">
          {document.title.map((token) =>formatToken(token))}
        </header>
        <section className="doc-content">
          {document.content.map((token) =>formatToken(token))}
          </section>
          <div className="guess-section">
          <input
            type="text"
            value={word}
            onChange={(e) => setWord(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Guess a word..."
          />
          <button ref={buttonRef} onClick={handleSubmitGuess} disabled={!word}>Submit Guess</button>
          {guesses.map((guess) => (
            <p>{guess.word}</p>
          ))}
        </div>
      </>
      ) : (
        <div className="loader">Loading...</div> 
      )}
    </div>
  );
}

export default App;
