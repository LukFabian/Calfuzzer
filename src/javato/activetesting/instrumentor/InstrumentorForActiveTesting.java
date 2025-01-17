package javato.activetesting.instrumentor;

import benchmarks.instrumented.java15.util.Arrays;
import javato.activetesting.common.Parameters;
import javato.instrumentor.RecursiveVisitor;
import javato.instrumentor.TransformClass;
import javato.instrumentor.Visitor;

/**
 * Copyright (c) 2007-2008,
 * Pallavi Joshi   <pallavi@cs.berkeley.edu>
 * All rights reserved.
 * <p/>
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 * <p/>
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 * <p/>
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * <p/>
 * 3. The names of the contributors may not be used to endorse or promote
 * products derived from this software without specific prior written
 * permission.
 * <p/>
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 * TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 * PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
 * OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
public class InstrumentorForActiveTesting {
    public static void main(String[] args) {
        String rt = System.getProperty("user.dir") + "/lib/rt.jar";
        System.setProperty("sun.boot.class.path", rt);
        System.setProperty("java.ext.dirs", rt);
        RecursiveVisitor vv = new RecursiveVisitor(null);
        VisitorForActiveTesting pv = new VisitorForActiveTesting(vv);
        vv.setNextVisitor(pv);
        Visitor.setObserverClass("javato.activetesting.analysis.ObserverForActiveTesting");
        TransformClass processor = new TransformClass();
        processor.processAllAtOnce(args, pv);
        Visitor.dumpIidToLine();
        pv.writeSymTblSize();
    }
}
