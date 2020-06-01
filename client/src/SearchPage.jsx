import React, { useState } from 'react';
import { Paper, Typography, Grid, TextField, Button } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import SearchIcon from '@material-ui/icons/Search';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    minHeight: '100vh',
    textAlign: "center",
    padding: theme.spacing(1),
  },
  paper: {
    minHeight: "100vh",
    backgroundImage: `url(${"/images/background_3.png"})`,
    backgroundRepeat: 'no-repeat',
    backgroundSize: 'cover'
  },
  title: {
    margin: theme.spacing(2),
    color: '#FFF'
  },
  searchBox: {
    width: "50%",
    margin: theme.spacing(1),
    backgroundColor: "#FFF"
  },
  distance: {
    width: "10%",
    margin: theme.spacing(1),
  },
  button: {
    margin: theme.spacing(1),
  }
}));

const SearchPage = () => {
  const classes = useStyles();
  const [q, setQ] = useState("");
  const [d, setD] = useState(5);

  return (
    <Paper className={classes.paper}>
      <Grid
        container
        spacing={0}
        alignItems="center"
        justify="center"
        className={classes.root}
      >
        <Grid item xs={12}>
          <Typography variant="h2" className={classes.title}>Erdős Graphwalker</Typography>
          <Typography variant="h5" className={classes.title}>Construct coauthorship graph and calculate distance between its nodes based on Erdős number</Typography>
          <TextField 
            id="outlined-search" 
            label="Enter your query" 
            value={q}
            onChange={(e) => { setQ(e.target.value) }}
            type="search" 
            variant="outlined" 
            className={classes.searchBox} 
          />
          <div>
            <Button
              variant="contained"
              color="primary"
              size="large"
              className={classes.button}
              href={`/search/${encodeURI(q)}`}
              endIcon={<SearchIcon />}
            >
              Search
            </Button>
          </div>
        </Grid>
      </Grid>;
    </Paper>
  );
};

export default SearchPage;