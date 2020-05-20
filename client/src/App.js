import React from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import SearchPage from './SearchPage';
import ListResults from './ListResults';
import DisplayResults from './DisplayResults';

const App = () => (
  <Router>
    <div>
      <Route exact path="/" component={SearchPage} />
      <Route exact path="/search/:name" component={ListResults} />
      <Route exact path="/author/:id" component={DisplayResults} />
    </div>
  </Router>
);

export default App;
