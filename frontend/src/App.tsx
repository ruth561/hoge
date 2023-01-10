import React, { useEffect } from 'react'

import logo from './logo.svg'
import './App.css'

const App = () => {
  const [text, setText] = React.useState('')

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch('/api')
      const data = await response.text()
      // responseとしてjsonを返す場合は、dataの定義は以下
      // const data = await response.json()
      setText(data)
    }
    fetchData().catch(console.error)
  }, [])

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        {text ? <p>{text} from our flask api 😀</p> : <p> Loading ... maybe server is not running</p>}
      </header>
    </div>
  )
}

export default App
