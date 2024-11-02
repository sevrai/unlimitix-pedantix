import { Token } from "./App";

export const transformText = (text: string, offset = 0): Token[] => {
    return text.split(' ').map((word, index, tokens) => ({
        id: (offset + index).toString(),
        length: word.length,
        display: Math.random() * 3 < 1 ? word : undefined,
        whitespace: index === tokens.length - 1 ? "\u000A" : '\u00A0'
    }));

}