// Implementation of the Network Animation Viewer Model
// George F. Riley, Georgia Tech, Spring 2009

#include <iostream>
#include "fsModel.h"

using namespace std;

// NetNode data/methods
fsNode::fsNode()
  : id(-1), x(0), y(0), z(0), shape(CIRCLE),
    visible(false), exists(false), lastPacketLbtxTime(0)
{ // Default constructor is only used when indexing the map of
  // all nodes with an invalid id; this gives a node with exists = false.
}

fsNode::fsNode(NodeId_t id0, Meters_t x0, Meters_t y0, Meters_t z0)
  : id(id0), x(x0), y(y0), z(z0), shape(CIRCLE),
    visible(true), exists(true), lastPacketLbtxTime(0)
{
}

void fsNode::SetShape(NodeShape_t s)
{
  shape = s;
}


void fsNode::Show()
{
  visible = true;
}

void fsNode::Hide()
{
  visible = false;
}

fsWiredLink fsNode::FindLink(NodeId_t n2Id)
{
  if (exists)
    {
      for (Size_t i = 0; i < links.size(); ++i)
        {
          if (links[i].n2 == n2Id) return links[i];
        }
    }
  // Not found, return empty link
  return fsWiredLink();
}

void fsNode::AddLink(const fsWiredLink& lk)
{
  links.push_back(lk);
}

QPointF fsNode::GetLoc2d() const
{
  return QPointF(x, y);
}

fsWiredLink::fsWiredLink()
  : exists(false)
{ // Allow an erroneous return from GetLink
}

fsWiredLink::fsWiredLink(NodeId_t nd1, NodeId_t nd2)
  : n1(nd1), n2(nd2), exists(true)
{
}

// Wired Packet Members and Methods

fsWiredPacket::fsWiredPacket(NodeId_t n1, NodeId_t n2,
                                 Time_t fbTx0, Time_t lbTx0,
                                 Time_t fbRx0, Time_t lbRx0)
  : fbTx(fbTx0), lbTx(lbTx0), fbRx(fbRx0), lbRx(lbRx0),
    txNode(n1), rxNode(n2)
{
}

// fsModel methods

// Constructor
fsModel::fsModel() : currentTime(0), view(nil)
{
  // Nothing else needed  
}

void fsModel::SetView(fsView* v)
{
  view = v;
}

QRectF fsModel::GetBoundingRect()
{
  QRectF br(topLeft, QPointF());
  // Add 10% borders
  float w = bottomRight.x() - topLeft.x();
  float h = bottomRight.y() - topLeft.y();
  br.setWidth (w * 1.1);
  br.setHeight(h * 1.1);
  br.moveTopLeft(topLeft - QPointF(w * 0.05, h * 0.05));
  return br;
}

// SetBoundingRect sets the minimum size of the network node placement.
// It will grow as needed as nodes are added
void fsModel::SetBoundingRect(QRectF br)
{
  topLeft = br.topLeft();
  bottomRight = br.bottomRight();
}

void fsModel::AddNode(NodeId_t id,
                             Meters_t x, Meters_t y, Meters_t z)
{
  //cout << "NN " << 0.0 << " " << x0 << " " << y0 << endl;
  if (topLeft == QPointF(0,0) && bottomRight == QPointF(0,0))
    { // First node, set ul and lr
      topLeft = QPointF(x, y);
      bottomRight = QPointF(x, y);
    }
  else
    {
      if (x < topLeft.x())  topLeft.setX(x);
      if (y < topLeft.y())  topLeft.setY(y);
      if (x > bottomRight.x()) bottomRight.setX(x);
      if (y > bottomRight.y()) bottomRight.setY(y);
    }
  allNodes[id] = fsNode(id, x, y, z);;
}

fsNode& fsModel::GetNode(NodeId_t id)
{ // Finds a node by id
  return allNodes[id];
}


void fsModel::AddDuplexLink(NodeId_t n1Id, NodeId_t n2Id)
{
  fsNode& n1 = GetNode(n1Id);
  fsNode& n2 = GetNode(n2Id);
  if (!n1.exists || !n2.exists)
    {
      cout << "fsModel::AddDuplexLink::AddDuplexLink failed" << endl;
      return;
    }
  allLinks.push_back(fsWiredLink(n1Id, n2Id));
  n1.AddLink(allLinks.back());
  allLinks.push_back(fsWiredLink(n2Id, n1Id));
  n2.AddLink(allLinks.back());
}

fsWiredLink fsModel::GetLink(NodeId_t n1, NodeId_t n2)
{
  fsNode& n = GetNode(n1);
  return n.FindLink(n2);
}


void fsModel::AddPacket(NodeId_t n1Id, NodeId_t n2Id,
                                  Time_t fbTx, Time_t lbTx,
                                  Time_t fbRx, Time_t lbRx)
{
  allPkts.insert(
          make_pair(lbRx, 
                    fsWiredPacket(n1Id, n2Id, fbTx, lbTx, fbRx, lbRx)));
}

// Time Management
void fsModel::AdvanceTime(Time_t t)
{
  currentTime += t;
  // Remove pkts that are in the past
  while(!allPkts.empty())
    {
      multimap<Time_t, fsWiredPacket>::iterator first = allPkts.begin();
      if (first->first > currentTime) return; // Still in future
      // Remove it
      allPkts.erase(allPkts.begin());
    }
}


  
