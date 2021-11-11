
import net.imagej.ImageJ;

ImageJ ij = new ImageJ();

for (p : ij.command().getPlugins()) {
	System.out.println(p);
}
