"""Bridge sanity tests: deterministic dependency closure, copy safety, GUID collisions."""
import json,tempfile,unittest
from pathlib import Path
from stage_r12_preview import run
SCENE="R12_Copacabana_Lojas_Vitrines_Entradas.unity"
A="a"*32
B="b"*32
C="c"*32
class BridgeTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory()
  self.addCleanup(self.t.cleanup)
  root=Path(self.t.name)
  self.visual=root/"source"
  self.game=root/"game"
  self.src=self.visual/"Assets"
  gameassets=self.game/"FacilityOps/Assets"
  (self.src/"Scenes").mkdir(parents=True)
  (self.src/"Materials").mkdir()
  (gameassets/"_Game/Scenes").mkdir(parents=True)
  scene=self.src/"Scenes"/SCENE
  scene.write_text("scene\nm_Material: {fileID: 2100000, guid: "+B+", type: 2}\n",encoding="utf8")
  (Path(str(scene)+".meta")).write_text("fileFormatVersion: 2\nguid: "+A+"\n",encoding="utf8")
  material=self.src/"Materials/a.mat"
  material.write_text("Material:\n shader: {fileID: 4800000, guid: "+C+", type: 3}\n",encoding="utf8")
  (Path(str(material)+".meta")).write_text("fileFormatVersion: 2\nguid: "+B+"\n",encoding="utf8")
  original=gameassets/"_Game/Scenes/ResortPrologue.unity"
  original.write_text("PLAYABLE_SOURCE_INTACT",encoding="utf8")
  (Path(str(original)+".meta")).write_text("fileFormatVersion: 2\nguid: "+"d"*32+"\n",encoding="utf8")
  self.original=original
 def test_dependency_closure_copy_and_idempotent(self):
  a=run(self.visual,self.game,True)
  self.assertEqual(a["asset_count"],2)
  self.assertEqual(a["unknown_external_or_unity_builtin_guids"],1)
  b=run(self.visual,self.game,False)
  self.assertEqual(a,b)
  self.assertEqual(self.original.read_text(encoding="utf8"),"PLAYABLE_SOURCE_INTACT")
  self.assertEqual(run(self.visual,self.game,False),a)
  self.assertTrue((self.game/"FacilityOps/Assets/_Game/Preview/CopacabanaR12/Scenes"/SCENE).is_file())
 def test_disallow_modified_staged_asset(self):
  run(self.visual,self.game,False)
  x=self.game/"FacilityOps/Assets/_Game/Preview/CopacabanaR12/Materials/a.mat"
  x.write_text("HACK",encoding="utf8")
  with self.assertRaisesRegex(RuntimeError,"WOULD_OVERWRITE_MODIFIED"):
   run(self.visual,self.game,False)
 def test_guid_collision_guards_gameplay(self):
  game_meta=self.game/"FacilityOps/Assets/_Game/Scenes/ResortPrologue.unity.meta"
  game_meta.write_text("fileFormatVersion: 2\nguid: "+B+"\n",encoding="utf8")
  with self.assertRaisesRegex(RuntimeError,"GAME_GUID_CONFLICT"):
   run(self.visual,self.game,False)
  self.assertEqual(self.original.read_text(encoding="utf8"),"PLAYABLE_SOURCE_INTACT")
if __name__=="__main__":unittest.main()
