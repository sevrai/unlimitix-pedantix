import { Guess, Document } from "./App";

export const fetchGuess = async (gameId: string, guess: string): Promise<Guess> => {
    const response = await fetch(`http://localhost:8000/api/game/${gameId}/guess/${guess}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return response.json();
}

export const fetchGame = async (gameId: string): Promise<Document> => {
    const response = await fetch(`http://localhost:8000/api/game/${gameId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return response.json();
}
