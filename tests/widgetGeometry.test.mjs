import {test} from 'node:test'
import assert from 'node:assert/strict'
import {dragBounds,clampPoint,relativePoint,restorePoint,snapPoint} from '../src/utils/widgetGeometry.js'
test('窄屏、横屏及大于可用区域的元素保持在可见边界',()=>{
  for(const [width,height]of[[320,740],[390,844],[844,390],[1440,1000]]){
    const b=dragBounds(width,height,160,64,80,20)
    const p=clampPoint({x:99999,y:-200},b)
    assert(p.x+160<=width&&p.y>=0&&p.y+64<=height)
  }
  assert.deepEqual(dragBounds(100,50,160,64,80,20),{left:0,right:0,top:0,bottom:0})
})
test('换方向后使用相对位置，右侧停靠不会跑出屏幕',()=>{
  const wide=dragBounds(1440,1000,136,64,80,20),phone=dragBounds(390,844,160,64,68,20)
  const saved=relativePoint({x:wide.right,y:(wide.top+wide.bottom)/2},wide)
  const restored=restorePoint(saved,phone)
  assert.equal(restored.x,phone.right)
  assert.equal(restored.y,(phone.top+phone.bottom)/2)
  assert.equal(restorePoint({x:'bad',y:1},phone),null)
})
test('边缘和网格吸附先检查边界，不引入越界值',()=>{
  const b=dragBounds(300,320,112,124)
  assert.equal(snapPoint({x:500,y:800},b,'edge').x,b.right)
  const p=snapPoint({x:b.right,y:b.bottom},b,'grid')
  assert(p.x<=b.right&&p.y<=b.bottom)
  assert.deepEqual(clampPoint({x:NaN,y:Infinity},b),{x:b.left,y:b.top})
})
