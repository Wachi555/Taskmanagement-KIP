const chai = require('chai');
const expect = chai.expect;
const request = require('supertest');
const app = require('../src/server');  // adjust path if needed

describe('App basic route tests', function() {
  it('GET / should return 200 and contain appName', async function () {
    const res = await request(app).get('/');
    expect(res.status).to.equal(200);
    expect(res.text).to.include('Notaufnahme Universitätsklinikum Regensburg');
  });

  it('GET /coordination should return 200 or 500 (depending on backend)', async function () {
    const res = await request(app).get('/coordination');
    expect([200, 500]).to.include(res.status);
  });

  it('GET /registration should return 200 or 500 (depending on backend)', async function () {
    const res = await request(app).get('/registration');
    expect([200, 500]).to.include(res.status);
  });

  it('GET /nonexistent should return 404', async function () {
    const res = await request(app).get('/nonexistent');
    expect(res.status).to.equal(404);
  });
});

