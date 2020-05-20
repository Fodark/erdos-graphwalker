import React from 'react';
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
  title: {
    margin: theme.spacing(2),
  },
  searchBox: {
    width: "50%",
    margin: theme.spacing(1),
  },
  distance: {
    width: "10%",
    margin: theme.spacing(1),
  },
  button: {
    margin: theme.spacing(1),
  }
}));

const App = () => {
  const classes = useStyles();

  return (
    <Paper style={{ minHeight: "100vh" }}>
      <Grid
        container
        spacing={0}
        alignItems="center"
        justify="center"
        className={classes.root}
      >
        <Grid item xs={12}>
          <Typography variant="h2" className={classes.title}>Nena Graphwalker</Typography>
          <TextField id="outlined-search" label="Enter your query" type="search" variant="outlined" className={classes.searchBox} />
          <TextField
            id="standard-number"
            label="Max distance"
            type="number"
            variant="outlined"
            defaultValue={5}
            className={classes.distance}
            InputLabelProps={{
              shrink: true,
            }}
          />
          <div>
            <Button
              variant="contained"
              color="primary"
              size="large"
              className={classes.button}
              endIcon={<SearchIcon />}
            >
              Search
            </Button>
          </div>
        </Grid>
      </Grid>;
    </Paper>
  )
};

export default App;
