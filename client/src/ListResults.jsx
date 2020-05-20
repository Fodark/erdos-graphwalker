import React, { useState, useEffect } from 'react';
import { Paper, CircularProgress, List, ListItem, ListItemText, Link, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import Avatar from '@material-ui/core/Avatar';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    minHeight: '100vh',
    textAlign: "center",
    padding: theme.spacing(1),
  },
  title: {
    margin: theme.spacing(2),
    fontWeight: "normal",
    display: "inline"
  },
  name: {
    fontWeight: "bold",
    display: "inline"
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
  },
  list: {
    marginLeft: theme.spacing(5),
  },
  listText: {
    fontSize: 28,
  },
  subListText: {
    fontSize: 24,
    color: "#BBB"
  },
  avatar: {
    width: theme.spacing(10),
    height: theme.spacing(10),
    marginRight: theme.spacing(3),
  }
}));

const ListResults = (props) => {
  const classes = useStyles();
  const [data, setData] = useState([]);
  const [status, setStatus] = useState(0);
  const name = props.match.params.name
  const distance = props.location.search.split('=')[1]

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(`/search?name=${name}`, {mode: 'cors',
        headers: {
          'Access-Control-Allow-Origin':'react'
        }});
      setStatus(res.status);
      const body = await res.json();
      console.log(body.data);
      setData(body.data);
    };

    if(status == 0) {
      fetchData()
    }
  }, data);

  const generateListItem = (id, name, affiliation, avatarUrl) => (
    <Link href={`/author/${id}`} key={id}>
      <ListItem>
        <ListItemAvatar>
          <Avatar className={classes.avatar} src={avatarUrl} />
        </ListItemAvatar>
        <ListItemText 
          primary={<Typography className={classes.listText}>{name}</Typography>} 
          secondary={<Typography className={classes.subListText}>{affiliation}</Typography>} 
        />
      </ListItem>
    </Link>
  );

  return (
    <Paper style={{minHeight: "100vh", textAlign: "center"}}>
      <div className={classes.root}>
      <Typography variant="h3" className={classes.title}>Results for</Typography>
      <Typography variant="h3" className={classes.name}>{name}</Typography>
      <List className={classes.list}>
        {status ? data.map(p => (
          generateListItem(p[0], p[1], p[2], "https://www.kirkleescollege.ac.uk/wp-content/uploads/2015/09/default-avatar.png")
        )) : <CircularProgress />}
      </List>
      </div>
    </Paper>
  );
};

export default ListResults;
