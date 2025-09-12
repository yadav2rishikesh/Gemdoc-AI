import React, { useState } from "react";
import { uploadFileAPI, askAPI } from "./api";

function App() {
    const [file, setFile] = useState(null);
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);
    const [darkMode, setDarkMode] = useState(false); // 🔥 dark mode state

    const handleUpload = async() => {
        if (!file) return alert("Select a file (.pdf or .docx)");
        setStatus("Uploading...");
        const res = await uploadFileAPI(file);
        setStatus(res.message || "Uploaded");
    };

    const handleAsk = async() => {
        if (!question) return alert("Enter a question");
        setLoading(true);
        const res = await askAPI(question, 3);
        setAnswer(res.answer || res.error || "No answer");
        setLoading(false);
    };

    return ( <
        div className = { darkMode ? "dark" : "" } >
        <
        div className = "max-w-2xl mx-auto mt-12 p-6 bg-white dark:bg-gray-900 dark:text-gray-200 shadow-md rounded-lg transition-colors" >

        { /* Dark Mode Toggle */ } <
        button onClick = {
            () => setDarkMode(!darkMode)
        }
        className = "float-right mb-4 px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-sm" > { darkMode ? "☀️ Light Mode" : "🌙 Dark Mode" } <
        /button>

        <
        h1 className = "text-3xl font-bold text-blue-600 dark:text-blue-400 mb-4" > 📄GEMDOC AI <
        /h1> <
        p className = "text-gray-600 dark:text-gray-400 mb-6" >
        Upload PDF / DOCX and ask questions(FastAPI backend + Gemini) <
        /p>

        { /* File Upload */ } <
        div className = "mb-6" >
        <
        input type = "file"
        accept = ".pdf,.docx"
        onChange = {
            (e) => setFile(e.target.files[0])
        }
        className = "block w-full border border-gray-300 rounded p-2 dark:bg-gray-800 dark:border-gray-600" /
        >
        <
        button onClick = { handleUpload }
        className = "mt-3 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" >
        Upload <
        /button> <
        div className = "mt-2 text-sm text-gray-500 dark:text-gray-400" > { status } < /div> < /
        div >

        { /* Ask Question */ } <
        div className = "mb-6" >
        <
        input value = { question }
        onChange = {
            (e) => setQuestion(e.target.value)
        }
        placeholder = "Ask a question..."
        className = "w-3/4 border border-gray-300 rounded p-2 dark:bg-gray-800 dark:border-gray-600" /
        >
        <
        button onClick = { handleAsk }
        className = "ml-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600" > { loading ? "Thinking..." : "Ask" } <
        /button> < /
        div >

        { /* Answer Section */ } {
            answer && ( <
                div className = "p-4 border border-gray-300 dark:border-gray-600 rounded bg-gray-50 dark:bg-gray-800" >
                <
                strong className = "text-gray-700 dark:text-gray-300" > Answer: < /strong> <
                p className = "mt-2 whitespace-pre-wrap" > { answer } < /p> < /
                div >
            )
        } <
        /div> < /
        div >
    );
}

export default App;