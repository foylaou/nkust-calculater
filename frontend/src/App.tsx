import Calculator from "./components/Calculator.tsx";
import TitleBar from "./components/TitleBar.tsx";

function App() {
  return (
    <div className="h-screen flex flex-col bg-[#36393f]">
      <TitleBar />
      <div className="flex-1 pt-12 overflow-auto">
        <Calculator />
      </div>
    </div>
  )
}

export default App
