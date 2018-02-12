import org.osm2world.core.target.obj.ObjWriter;

import static com.google.common.base.Preconditions.checkArgument;
import static java.lang.String.format;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintStream;
import java.util.Iterator;

import org.osm2world.core.GlobalValues;
import org.osm2world.core.map_data.creation.MapProjection;
import org.osm2world.core.map_data.data.MapData;
import org.osm2world.core.math.VectorXYZ;
import org.osm2world.core.math.VectorXZ;
import org.osm2world.core.target.TargetUtil;
import org.osm2world.core.target.common.rendering.Camera;
import org.osm2world.core.target.common.rendering.Projection;

/**
 * utility class for creating an Wavefront OBJ file
 */
public final class ObjIdWriter {

	public static final void writeObjFile(
			File objFile, MapData mapData,
			MapProjection mapProjection,
			Camera camera, Projection projection, boolean underground)
			throws IOException {
		
		if (!objFile.exists()) {
			objFile.createNewFile();
		}
		
		File mtlFile = new File(objFile.getAbsoluteFile() + ".mtl");
		if (!mtlFile.exists()) {
			mtlFile.createNewFile();
		}
		
		PrintStream objStream = new PrintStream(objFile);
		PrintStream mtlStream = new PrintStream(mtlFile);
		
		/* write comments at the beginning of both files */
		
		writeObjHeader(objStream, mapProjection);
		
		writeMtlHeader(mtlStream);
				
		/* write path of mtl file to obj file */
		
		objStream.println("mtllib " + mtlFile.getName() + "\n");
		
		/* write actual file content */
		
		ObjIdTarget target = new ObjIdTarget(objStream, mtlStream);
                
		TargetUtil.renderWorldObjects(target, mapData, underground);
		
		objStream.close();
		mtlStream.close();
	}
	
	private static final void writeObjHeader(PrintStream objStream,
			MapProjection mapProjection) {
		
		objStream.println("# This file was created by OSM2World "
				+ GlobalValues.VERSION_STRING + " - "
				+ GlobalValues.OSM2WORLD_URI + "\n");
		objStream.println("# Projection information:");
		objStream.println("# Coordinate origin (0,0,0): "
				+ "lat " + mapProjection.calcLat(VectorXZ.NULL_VECTOR) + ", "
				+ "lon " + mapProjection.calcLon(VectorXZ.NULL_VECTOR) + ", "
				+ "ele 0");
		objStream.println("# North direction: " + new VectorXYZ(
						mapProjection.getNorthUnit().x, 0,
						- mapProjection.getNorthUnit().z));
		objStream.println("# 1 coordinate unit corresponds to roughly "
				+ "1 m in reality\n");
		
	}

	private static final void writeMtlHeader(PrintStream mtlStream) {
		
		mtlStream.println("# This file was created by OSM2World "
				+ GlobalValues.VERSION_STRING + " - "
				+ GlobalValues.OSM2WORLD_URI + "\n\n");
		
	}
			
}