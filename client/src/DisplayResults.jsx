import React, { useState, useEffect } from 'react';
import { Grid, CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@material-ui/core';
import {Sigma, RandomizeNodePositions, RelativeSize} from 'react-sigma';

const DisplayResults = (props) => {
  const id = props.match.params.id;
  const [status, setStatus] = useState(0);
  const [graph, setGraph] = useState({});
  const [rows, setRows] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`/author?id=${id}`);
      const body = await response.json();
      const data = body.data;

      let n = [];
      let e = [];
      let r = [];

      function createData(n, d) {
        return { n, d };
      }
      
      data.forEach((coauthor, idx) => {
        n.push({ 'id': coauthor.end_node_id, 'label': `${coauthor.end_node_name}: ${coauthor.distance}`, 'color': idx === 0 ? "#F00" : "#000" })
        if(coauthor.distance > 0) {
          r.push(createData(coauthor.end_node_name, coauthor.distance));
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
    <div>
    {status ? 
      <div style={{width: 'inherit', height: '100vh', maxHeight: '100vh'}}> 
        <Grid container style={{height: 'inherit'}}>
          <Grid item xs={12} lg={8}>
            <Sigma graph={graph} settings={{drawEdges: true, clone: false, labelThreshold: 20}} style={{width:"100%", height:"100%"}}>
              <RelativeSize initialSize={200}/>
              <RandomizeNodePositions/>
            </Sigma>
          </Grid>
          <Grid item lg={4} style={{height: 'inherit', maxHeight: 'inherit'}}>
            <TableContainer component={Paper}>
              <Table size="small" aria-label="a dense table">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell align="right">Distance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {rows.map((row) => (
                    <TableRow key={row.name}>
                      <TableCell component="th" scope="row">
                        {row.name}
                      </TableCell>
                      <TableCell align="left">{row.n}</TableCell>
                      <TableCell align="right">{row.d}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>
      </div>
      : <CircularProgress />}
    </div>
  );
};

export default DisplayResults;