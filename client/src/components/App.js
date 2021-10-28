import "./App.css";

import NavBar from "./NavBar";
import MainContent from './MainContent';
import Footer from "./Footer";

const dropdowns = 
  [
    {title: "View", endpoint: "view"},
    {title: "Insert", endpoint: "insert"}
  ];

function App() {
  return (
    <div className="App">
        <NavBar dropdowns={dropdowns} title="MICHELANGELO" />
        <MainContent />
        <Footer 
            author="Victor Moraes"
            madeWith="☕"
            gitHub="https://github.com/moraesvic/michelangelo"
        />
    </div>
  );
}

export default App;
