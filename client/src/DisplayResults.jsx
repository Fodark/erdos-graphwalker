import React, { useState, useEffect } from 'react';
import { Grid, CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from '@material-ui/core';
import {Sigma, RandomizeNodePositions, RelativeSize} from 'react-sigma';

const DisplayResults = (props) => {
  const id = props.match.params.id;
  const isGoogle = !parseInt(id)
  const [status, setStatus] = useState(0);
  const [graph, setGraph] = useState({});
  const [rows, setRows] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      let response
      if(isGoogle)
        response = await fetch(`/author?id=${id}`);
      else 
        response = await fetch(`/author?node_id=${id}`);
      const body = await response.json();
      const data = body.data;
      //console.log(data);

      let n = [];
      let e = [];
      let r = [];

      function createData(n, d, a) {
        return { n, d, a };
      }
      
      data.forEach((coauthor, idx) => {
        n.push({ 'id': coauthor.end_node_id, 'label': `${coauthor.end_node_name}: ${coauthor.distance}`, 'color': idx === 0 ? "#F00" : "#000" })
        if(coauthor.distance > 0) {
          r.push(createData(coauthor.end_node_name, coauthor.distance, coauthor.affiliation));
          for(let i = 0; i < coauthor.path.length - 1; i++) {
            e.push({id: `${coauthor.end_node_id}${i}`, 'source': coauthor.path[i], 'target': coauthor.path[i+1] });
          }
        }
      });
      
      setGraph({'nodes': n, 'edges': e});
      setRows(r);
      setStatus(response.status);
    };

    if(status === 0){
      fetchData();
    }
  }, [status]);

  return (
    <div style={{height: '100vh'}}>
    {status === 200 && rows.length !== 0 ? 
      <div style={{width: 'inherit', height: '100vh', maxHeight: '100vh'}}> 
        <Grid container style={{height: 'inherit'}}>
          <Grid item xs={12} lg={8}>
            <Sigma graph={graph} settings={{drawEdges: true, clone: false, labelThreshold: 20}} style={{width:"100%", height:"100%"}}>
              <RelativeSize initialSize={200}/>
              <RandomizeNodePositions/>
            </Sigma>
          </Grid>
          <Grid item lg={4} style={{height: 'inherit', maxHeight: '100vh'}}>
            <TableContainer component={Paper} style={{maxHeight: 'inherit', backgroundColor: "#145214"}}>
              <Table size="small" aria-label="a dense table">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell align="right">Distance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {rows.map((row) => (
                    <TableRow key={row.name} key={row.n}>
                      <TableCell component="th" scope="row" style={{color: "#FFF"}}>
                        {row.name}
                      </TableCell>
                      <TableCell align="left">{
                        <div>
                          <Typography style={{color: "#FFF"}}>{row.n}</Typography>
                          <Typography variant="subtitle1" style={{color: "#FFF"}}>{row.a}</Typography>
                        </div>}</TableCell>
                      <TableCell align="right" style={{color: "#FFF"}}>{row.d || ""}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>
      </div>
      : status === 202 || (status === 200 && rows.length === 0) ? 
        <div style={{textAlign: 'center', position: 'relative', top: '40%'}}>
          <Typography variant="h3">This author is not currently available on our system</Typography>
          <Typography variant="h3">Data are being collected, come back in a few minutes</Typography>
        </div> : <CircularProgress />}
    </div>
  );
};

export default DisplayResults;